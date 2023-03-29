from pydantic import BaseModel
from typing import Optional, List
import datetime


class StrictBaseModel(BaseModel):  # https://github.com/tiangolo/fastapi/issues/269
    class Config:
        extra = "forbid"


class User(BaseModel):
    user_name: str
    email_address: str
    password: str
    full_name: str
    unit_weight: Optional[str]


class AccessToken(BaseModel):
    token_id: Optional[int]
    user_id: Optional[int]
    token: str
    expiry_time: datetime.datetime


class UpdatedUser(StrictBaseModel):
    user_name: Optional[str]
    email_address: Optional[str]
    full_name: Optional[str]
    unit_weight: Optional[str]


class Exercise(BaseModel):
    exercise_id: int
    workout_exercise_id: int
    exercise_name: str
    min_reps: int
    max_reps: int
    muscle_group: str
    muscle_subgroup: str
    compound: bool
    completed: Optional[bool]
    workout_exercise_number: int


class Workout(BaseModel):
    workout_id: Optional[int]
    workout_number: int
    workout_name: str
    exercise_list: List[Exercise]


class WorkoutPlan(BaseModel):
    workout_plan_id: Optional[int]
    workout_plan_name: str
    workout_plan_type: str
    workout_plan_goal: str
    workout_list: List[Workout]
    last_workout: Optional[int]
