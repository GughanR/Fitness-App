from pydantic import BaseModel
from typing import Optional
import datetime


class StrictBaseModel(BaseModel):  # https://github.com/tiangolo/fastapi/issues/269
    class Config:
        extra = "forbid"
class User(BaseModel):
    user_id: Optional[int]
    user_name: str
    email_address: str
    password: str
    full_name: str
    unit_weight: Optional[str]

class Access_Token(BaseModel):
    token_id: Optional[int]
    user_id: Optional[int]
    token: str
    expiry_time: datetime.datetime

class Updated_User(StrictBaseModel):
    user_name: Optional[str]
    email_address: Optional[str]
    full_name: Optional[str]
    unit_weight: Optional[str]