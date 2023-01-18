from pydantic import BaseModel
from typing import Optional
import datetime

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