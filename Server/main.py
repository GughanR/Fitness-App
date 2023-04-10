from fastapi import FastAPI, Depends, Response, status, HTTPException
import schemas
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, and_, or_, delete
import random
import json
import string
import datetime
import email_manager

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


def generate_code():
    return random.randint(100000, 999999)


def check_verification(email, code):
    with open("new_emails.json", "r+", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
        except json.decoder.JSONDecodeError:
            data = {}
        try:
            correct_code = data[email]
        except Exception:
            return False
        if code == correct_code:
            return True
        else:
            return False


def generate_access_token():
    alphabet = string.ascii_letters
    numbers = string.digits
    punctuation = string.punctuation
    alphanumeric = alphabet + numbers + punctuation
    access_token = ''
    for i in range(50):
        access_token += random.choice(alphanumeric)
    return access_token


def check_valid_token(db, token):
    try:
        statement_2 = (
            select(models.AccessToken.expiry_time)
            .where(models.AccessToken.token == token)
        )
        expiry_time = db.scalars(statement_2).one()

        if expiry_time >= datetime.datetime.now():
            return True
        else:
            return False


    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Invalid token.")


@app.post("/user/create/add", status_code=status.HTTP_200_OK)
def add_new_user(request: schemas.User, db: Session = Depends(get_db)):
    code = generate_code()
    new_data = {
        request.email_address: code
    }

    email_manager.send_verification(request.email_address, code)

    with open("new_emails.json", "r+", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
        except json.decoder.JSONDecodeError:
            data = {}

    with open("new_emails.json", "w+") as json_file:
        data.update(new_data)
        json.dump(data, json_file, indent=4)

    return {"detail": "success"}


@app.post("/user/create/verify", status_code=status.HTTP_200_OK)
def verify_new_user(request: schemas.User, verification_code: int, db: Session = Depends(get_db)):
    new_user = models.User(
        user_name=request.user_name,
        email_address=request.email_address,
        password=request.password,
        full_name=request.full_name,
        unit_weight="KG"
    )

    if check_verification(request.email_address, verification_code):
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Users already exists."
            )
        return new_user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect code.")


@app.get("/user/login", status_code=status.HTTP_200_OK)
def user_login(username: str, password: str, db: Session = Depends(get_db)):
    # users = db.query(models.User).filter_by(user_name=username, password=password).all()
    statement = (
        select(models.User)
        .where(
            or_(
                models.User.user_name == username,
                models.User.email_address == username
            ),
            models.User.password == password
        )
    )
    try:
        user = db.scalars(statement).one()

        access_token = models.AccessToken(
            user_id=user.user_id,
            token=generate_access_token(),
            expiry_time=datetime.datetime.now() + datetime.timedelta(hours=6)
        )
        try:
            db.add(access_token)
            db.commit()
            db.refresh(access_token)
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot create token.")
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")

    return access_token


@app.post("/user/login/forgot", status_code=status.HTTP_200_OK)
def forgot_password(email_address: str, db: Session = Depends(get_db)):
    new_password = generate_code()
    statement = (
        update(models.User)
        .where(models.User.email_address == email_address)
        .values(password=new_password)
    )
    try:
        db.execute(statement)
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User does not exist.")
    return {"detail": "success"}


@app.get("/user/details", status_code=status.HTTP_200_OK)
def get_user_details(token: str, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement_2 = (
        select(models.User)
        .join(models.User.access_token)
        .where(models.AccessToken.token == token)
    )
    try:
        user = db.scalars(statement_2).one()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error.")

    return user


@app.put("/user/update/details", status_code=status.HTTP_200_OK)
def update_details(token: str, user: schemas.UpdatedUser, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    user_details = get_user_details(token=token, db=db)
    print(user_details.user_name)

    for key, value in dict(user).items():
        if value:
            exec(f'user_details.{key} = value')

    statement = (
        update(models.User)
        .where(models.User.user_id == user_details.user_id)
        .values(
            user_name=user_details.user_name,
            full_name=user_details.full_name,
            email_address=user_details.email_address,
            unit_weight=user_details.unit_weight
        )
    )

    db.execute(statement)
    db.commit()

    return {"detail": "success"}


@app.put("/user/update/password", status_code=status.HTTP_200_OK)
def update_password(token: str, old_password: str, new_password: str, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    user_details = get_user_details(token=token, db=db)
    print(user_details.user_name)

    statement_1 = (
        select(models.User.user_id)
        .join(models.AccessToken)
        .where(
            models.AccessToken.token == token,
            models.User.password == old_password
        )
    )

    try:
        user_id = db.scalars(statement_1).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials entered.")

    statement_2 = (
        update(models.User)
        .where(models.User.user_id == user_id)
        .values(password=new_password)
    )

    try:
        db.execute(statement_2)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error.")

    return {"detail": "success"}


@app.put("/user/logout", status_code=status.HTTP_200_OK)
def logout(token: str, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        update(models.AccessToken)
        .where(models.AccessToken.token == token)
        .values(expiry_time=datetime.datetime.now())
    )
    try:
        db.execute(statement)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error.")

    return {"detail": "success"}


@app.get("/exercises", status_code=status.HTTP_200_OK)
def get_exercises(token: str, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        select(models.Exercise)
    )
    try:
        exercises = db.scalars(statement).all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return exercises


@app.post("/workout/plan/add", status_code=status.HTTP_200_OK)
def add_workout_plan(token: str, workout_plan: schemas.WorkoutPlan, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        select(models.User.user_id)
        .join(models.AccessToken)
        .where(models.AccessToken.token == token)
    )
    try:
        # Get user id
        user_id = db.scalars(statement).one()
        # Add workout plan details
        statement = (
            update(models.WorkoutPlan)
            .where(models.WorkoutPlan.user_id == user_id)
            .values(
                user_id=user_id,
                workout_plan_name=workout_plan.workout_plan_name,
                workout_plan_type=workout_plan.workout_plan_type,
                workout_plan_goal=workout_plan.workout_plan_goal
            )
        )
        new_workout_plan = models.WorkoutPlan(
            user_id=user_id,
            workout_plan_name=workout_plan.workout_plan_name,
            workout_plan_type=workout_plan.workout_plan_type,
            workout_plan_goal=workout_plan.workout_plan_goal
        )
        db.add(new_workout_plan)
        db.commit()
        db.refresh(new_workout_plan)

        # Add each workout
        for workout in workout_plan.workout_list:
            new_workout = models.Workout(
                workout_plan_id=new_workout_plan.workout_plan_id,
                workout_number=workout.workout_number,
                workout_name=workout.workout_name
            )
            db.add(new_workout)
            db.commit()
            db.refresh(new_workout)
            # Add each exercise
            for exercise in workout.exercise_list:
                new_exercise = models.WorkoutExercise(
                    workout_id=new_workout.workout_id,
                    exercise_id=exercise.exercise_id,
                    workout_exercise_number=exercise.workout_exercise_number
                )
                db.add(new_exercise)
                db.commit()
                db.refresh(new_exercise)
                print(new_exercise.workout_exercise_id)

        return {"detail": "success"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return user_id


@app.get("/workout-plan", status_code=status.HTTP_200_OK)
def get_workout_plans(token: str, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        select(models.WorkoutPlan)
        .join(models.User)
        .join(models.AccessToken)
        .where(models.AccessToken.token == token)
    )
    try:
        workout_plans = db.scalars(statement).all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return workout_plans


@app.get("/workout", status_code=status.HTTP_200_OK)
def get_workouts(token: str, workout_plan_id: int, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        select(models.Workout)
        .join(models.WorkoutPlan)
        .join(models.User)
        .join(models.AccessToken)
        .where(
            models.Workout.workout_plan_id == workout_plan_id,
            models.AccessToken.token == token
        )
    )
    try:
        workout_plans = db.scalars(statement).all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return workout_plans


@app.get("/workout-exercise", status_code=status.HTTP_200_OK)
def get_workout_exercises(token: str, workout_id: int, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    statement = (
        select(
            models.Exercise.exercise_id,
            models.Exercise.exercise_name,
            models.Exercise.min_reps,
            models.Exercise.max_reps,
            models.Exercise.muscle_group,
            models.Exercise.muscle_subgroup,
            models.Exercise.compound,
            models.WorkoutExercise.workout_exercise_id,
            models.WorkoutExercise.workout_exercise_number
        )
        .join(models.WorkoutExercise)
        .join(models.Workout)
        .join(models.WorkoutPlan)
        .join(models.User)
        .join(models.AccessToken)
        .where(
            models.WorkoutExercise.workout_id == workout_id,
            models.AccessToken.token == token
        )
    )
    try:
        workout_exercises = db.execute(statement).all()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return workout_exercises


@app.put("/workout-plan", status_code=status.HTTP_200_OK)
def update_workout_plan(token: str, updated_plan: schemas.WorkoutPlan, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout plan and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .where(
            models.WorkoutPlan.workout_plan_id == updated_plan.workout_plan_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    statement = (
        update(models.WorkoutPlan)
        .where(models.WorkoutPlan.workout_plan_id == updated_plan.workout_plan_id)
        .values(
            workout_plan_name=updated_plan.workout_plan_name,
            workout_plan_goal=updated_plan.workout_plan_goal
        )
    )
    try:
        db.execute(statement)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.put("/workout", status_code=status.HTTP_200_OK)
def update_workout(token: str, updated_workout: schemas.Workout, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .where(
            models.Workout.workout_id == updated_workout.workout_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    statement = (
        update(models.Workout)
        .where(models.Workout.workout_id == updated_workout.workout_id)
        .values(
            workout_name=updated_workout.workout_name
        )
    )
    try:
        db.execute(statement)
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.delete("/workout-plan", status_code=status.HTTP_200_OK)
def delete_workout_plan(token: str, plan_to_delete: schemas.WorkoutPlan, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout plan and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .where(
            models.WorkoutPlan.workout_plan_id == plan_to_delete.workout_plan_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")
    # Get workout exercise ids
    statement = (
        select(models.WorkoutExercise.workout_exercise_id)
        .join(models.Workout)
        .where(models.Workout.workout_plan_id == plan_to_delete.workout_plan_id)
    )
    try:
        workout_exercises = db.scalars(statement).all()
        # Remove relationship between workout_exercise and workout_exercise_history
        statement = (
            update(models.WorkoutExerciseHistory)
            .where(models.WorkoutExerciseHistory.workout_exercise_id.in_(workout_exercises))
            .values(workout_exercise_id=None)
        )
        db.execute(statement)
        db.commit()

        # Delete workout exercises
        statement = (
            delete(models.WorkoutExercise)
            .where(models.WorkoutExercise.workout_exercise_id.in_(workout_exercises))
        )
        db.execute(statement)
        db.commit()

        # Delete workout
        statement = (
            delete(models.Workout)
            .where(models.Workout.workout_plan_id == plan_to_delete.workout_plan_id)
        )
        db.execute(statement)
        db.commit()

        # Delete workout plan
        statement = (
            delete(models.WorkoutPlan)
            .where(models.WorkoutPlan.workout_plan_id == plan_to_delete.workout_plan_id)
        )
        db.execute(statement)
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.delete("/workout-exercise", status_code=status.HTTP_200_OK)
def delete_exercise(token: str, exercise_to_delete: schemas.Exercise, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that exercise and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .join(models.WorkoutExercise)
        .where(
            models.WorkoutExercise.workout_exercise_id == exercise_to_delete.workout_exercise_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    try:
        # Remove relationship between workout_exercise and workout_exercise_history
        statement = (
            update(models.WorkoutExerciseHistory)
            .where(models.WorkoutExerciseHistory.workout_exercise_id == exercise_to_delete.workout_exercise_id)
            .values(workout_exercise_id=None)
        )
        db.execute(statement)
        db.commit()

        # Get workout_id of deleted workout exercise (needed to reorder exercises)
        statement = (
            select(models.WorkoutExercise.workout_id)
            .where(models.WorkoutExercise.workout_exercise_id == exercise_to_delete.workout_exercise_id)
        )
        deleted_workout_id = db.scalars(statement).one()

        # Delete workout exercise
        statement = (
            delete(models.WorkoutExercise)
            .where(models.WorkoutExercise.workout_exercise_id == exercise_to_delete.workout_exercise_id)
        )
        db.execute(statement)
        db.commit()

        # Reorder workout exercises
        statement = (
            update(models.WorkoutExercise)
            .where(
                models.WorkoutExercise.workout_id == deleted_workout_id,
                models.WorkoutExercise.workout_exercise_number > exercise_to_delete.workout_exercise_number
            )
            .values(workout_exercise_number=models.WorkoutExercise.workout_exercise_number-1)
        )

        db.execute(statement)
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.delete("/workout", status_code=status.HTTP_200_OK)
def delete_workout(token: str, workout_to_delete: schemas.Workout, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .where(
            models.Workout.workout_id == workout_to_delete.workout_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")
    # Get workout exercise ids
    statement = (
        select(models.WorkoutExercise.workout_exercise_id)
        .join(models.Workout)
        .where(models.Workout.workout_id == workout_to_delete.workout_id)
    )
    try:
        workout_exercises = db.scalars(statement).all()
        # Remove relationship between workout_exercise and workout_exercise_history
        statement = (
            update(models.WorkoutExerciseHistory)
            .where(models.WorkoutExerciseHistory.workout_exercise_id.in_(workout_exercises))
            .values(workout_exercise_id=None)
        )
        db.execute(statement)
        db.commit()

        # Get workout_plan_id of deleted workout (needed to reorder workouts)
        statement = (
            select(models.Workout.workout_plan_id)
            .where(models.Workout.workout_id == workout_to_delete.workout_id)
        )
        deleted_workout_plan_id = db.scalars(statement).one()

        # Delete workout exercises
        statement = (
            delete(models.WorkoutExercise)
            .where(models.WorkoutExercise.workout_exercise_id.in_(workout_exercises))
        )
        db.execute(statement)
        db.commit()

        # Delete workout
        statement = (
            delete(models.Workout)
            .where(models.Workout.workout_id == workout_to_delete.workout_id)
        )
        db.execute(statement)
        db.commit()

        # Reorder workouts
        statement = (
            update(models.Workout)
            .where(
                models.Workout.workout_plan_id == deleted_workout_plan_id,
                models.Workout.workout_number > workout_to_delete.workout_number
            )
            .values(workout_number=models.Workout.workout_number - 1)
        )

        db.execute(statement)
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.post("/workout", status_code=status.HTTP_200_OK)
def add_workout(token: str, workout_plan_id, workout: schemas.Workout, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout plan and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .where(
            models.WorkoutPlan.workout_plan_id == workout_plan_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    new_workout = models.Workout(
        workout_plan_id=workout_plan_id,
        workout_number=workout.workout_number,
        workout_name=workout.workout_name
    )
    try:
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.post("/workout-exercise", status_code=status.HTTP_200_OK)
def add_workout_exercise(token: str, workout_id: int, exercise_id: int, num: int, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .where(
            models.Workout.workout_id == workout_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    new_workout_exercise = models.WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        workout_exercise_number=num
    )
    try:
        db.add(new_workout_exercise)
        db.commit()
        db.refresh(new_workout_exercise)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}


@app.post("/workout-exercise-history", status_code=status.HTTP_200_OK)
def add_workout_exercise_history(token: str, workout_exercise_id: int, db: Session = Depends(get_db)):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .join(models.WorkoutExercise)
        .where(
            models.WorkoutExercise.workout_exercise_id == workout_exercise_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    new_workout_exercise_history = models.WorkoutExerciseHistory(
        workout_exercise_id=workout_exercise_id,
        sets_completed=0,
        date_completed=datetime.datetime.now()
    )
    try:
        db.add(new_workout_exercise_history)
        db.commit()
        db.refresh(new_workout_exercise_history)
        new_id = new_workout_exercise_history.exercise_history_id
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success", "exercise_history_id": new_id}


@app.post("/set-history", status_code=status.HTTP_200_OK)
def add_set_history(
        token: str,
        exercise_history_id: int,
        set_number: int,
        reps_completed: int,
        weight_used: float,
        unit_weight: str,
        db: Session = Depends(get_db)
):
    if not check_valid_token(db, token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access expired.")

    # Check that workout and access token match to same user
    statement = (
        select(models.User)
        .join(models.AccessToken)
        .join(models.WorkoutPlan)
        .join(models.Workout)
        .join(models.WorkoutExercise)
        .join(models.WorkoutExerciseHistory)
        .where(
            models.WorkoutExerciseHistory.exercise_history_id == exercise_history_id,
            models.AccessToken.token == token
        )
    )
    try:
        # Only one value can be returned
        user = db.scalars(statement).one()
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden activity.")

    new_set_history = models.SetHistory(
        exercise_history_id=exercise_history_id,
        set_number=set_number,
        reps_completed=reps_completed,
        weight_used=weight_used,
        unit_weight=unit_weight
    )
    try:
        db.add(new_set_history)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    # Increment sets completed by 1
    statement = (
        update(models.WorkoutExerciseHistory)
        .where(
            models.WorkoutExerciseHistory.exercise_history_id == exercise_history_id
        )
        .values(sets_completed=(models.WorkoutExerciseHistory.sets_completed + 1))
    )
    try:
        db.execute(statement)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")

    return {"detail": "success"}
