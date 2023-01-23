from fastapi import FastAPI, Depends, Response, status, HTTPException
import schemas
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
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
            data={}
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


@app.post("/user/create/add", status_code=status.HTTP_200_OK)
def add_new_user(request: schemas.User, db: Session = Depends(get_db)):

    code  = generate_code()
    new_data = {
            request.email_address: code
        }

    email_manager.send_verification(request.email_address, code)

    with open("new_emails.json", "r+", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
        except json.decoder.JSONDecodeError:
            data={}

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
        unit_weight=request.unit_weight
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

@app.post("/user")
def test2(access_token: schemas.Access_Token, db: Session = Depends(get_db)):

    statement = (
        select(models.User)
        .join(models.User.access_token)
        .where(models.Access_Token.token_id == access_token.token_id)
    )
    users = db.scalars(statement).all()
        
    return users

@app.get("/user/login/username", status_code=status.HTTP_200_OK)
def user_login(username: str, password:str, db: Session = Depends(get_db)):

    users = db.query(models.User).filter_by(user_name=username, password=password).all()
    
    if len(users) != 0:
        print(users[0].user_id)
        access_token = models.Access_Token(
            user_id = users[0].user_id,
            token = generate_access_token(),
            expiry_time = datetime.datetime.now() + datetime.timedelta(hours=6)
            )
        try:
            db.add(access_token)
            db.commit()
            db.refresh(access_token)
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot create token.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")

    return access_token

@app.get("/user/login/email", status_code=status.HTTP_200_OK)
def user_login(email_address: str, password:str, db: Session = Depends(get_db)):
    users = db.query(models.User).filter_by(email_address=email_address, password=password).all()
    
    if len(users) != 0:
        print(users[0].user_id)
        access_token = models.Access_Token(
            user_id = users[0].user_id,
            token = generate_access_token(),
            expiry_time = datetime.datetime.now() + datetime.timedelta(hours=6)
            )
        try:
            db.add(access_token)
            db.commit()
            db.refresh(access_token)
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot create token.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials.")

    return access_token

@app.post("/user/login/forgot", status_code=status.HTTP_200_OK)
def forgot_password(email_address: str, db: Session = Depends(get_db)):
    new_password = generate_code()
    statement = (
        update(models.User)
        .where(models.User.email_address == email_address)
        .values(password = new_password)
    )
    try:
        db.execute(statement)
        db.commit()

    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User does not exist.")
    return {"detail": "success"}

@app.get("/user/details", status_code=status.HTTP_200_OK)
def get_user_details(token: str, db: Session = Depends(get_db)):
    statement = (
        select(models.User)
        .join(models.User.access_token)
        .where(models.Access_Token.token == token)
    )
    user = db.scalars(statement).one()
    
    return user