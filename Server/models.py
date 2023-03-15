from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
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

    access_token = relationship("Access_Token", back_populates="user")


class Access_Token(Base):
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
