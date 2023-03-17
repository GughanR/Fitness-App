from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(50), nullable=False, unique=True)
    email_address = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    full_name = Column(String(50), nullable=False)
    unit_weight = Column(String(50), nullable=False)

    access_token = relationship("AccessToken", back_populates="user")
    workout_plan = relationship("WorkoutPlan", back_populates="user")


class AccessToken(Base):
    __tablename__ = "access_token"
    token_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    token = Column(String(50), nullable=False, unique=True)
    expiry_time = Column(DateTime(), nullable=False)

    user = relationship("User", back_populates="access_token")


class Exercise(Base):
    __tablename__ = "exercise"
    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(50), nullable=False, unique=True)
    min_reps = Column(Integer, nullable=False)
    max_reps = Column(Integer, nullable=False)
    muscle_group = Column(String(50), nullable=False)
    muscle_subgroup = Column(String(50), nullable=True)
    compound = Column(Boolean)

    workout_exercise = relationship("WorkoutExercise", back_populates="exercise")


class WorkoutPlan(Base):
    __tablename__ = "workout_plan"
    workout_plan_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"))
    workout_plan_name = Column(String(50), nullable=False)
    workout_plan_type = Column(String(20), nullable=False)
    workout_plan_goal = Column(String(10), nullable=False)

    user = relationship("User", back_populates="workout_plan")
    workout = relationship("Workout", back_populates="workout_plan")


class Workout(Base):
    __tablename__ = "workout"
    workout_id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plan.workout_plan_id"))
    workout_number = Column(Integer, nullable=False)
    workout_name = Column(String(50), nullable=False)

    workout_plan = relationship("WorkoutPlan", back_populates="workout")
    workout_exercise = relationship("WorkoutExercise", back_populates="workout")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercise"
    workout_exercise_id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workout.workout_id"))
    workout_exercise_number = Column(Integer, nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id"))

    workout = relationship("Workout", back_populates="workout_exercise")
    exercise = relationship("Exercise", back_populates="workout_exercise")
    workout_exercise_history = relationship("WorkoutExerciseHistory", back_populates="workout_exercise")


class WorkoutExerciseHistory(Base):
    __tablename__ = "workout_exercise_history"
    exercise_history_id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercise.workout_exercise_id"))
    sets_completed = Column(Integer, nullable=False)
    date_completed = Column(DateTime(), nullable=False)

    workout_exercise = relationship("WorkoutExercise", back_populates="workout_exercise_history")
    set_history = relationship("SetHistory", back_populates="workout_exercise_history")


class SetHistory(Base):
    __tablename__ = "set_history"
    set_history_id = Column(Integer, primary_key=True, index=True)
    exercise_history_id = Column(Integer, ForeignKey("workout_exercise_history.exercise_history_id"))
    set_number = Column(Integer, nullable=False)
    reps_completed = Column(Integer, nullable=False)
    weight_used = Column(Float(5), nullable=False)
    unit_weight = Column(String(10), nullable=False)

    workout_exercise_history = relationship("WorkoutExerciseHistory", back_populates="set_history")

