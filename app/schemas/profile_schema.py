from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class GetProfileId(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    user_permission: bool
    user_comments: int
    user_reg_date: date
    user_study_year: int


class GetProfileIdPic(BaseModel):
    user_photo: bytes

    class Config:
        arbitrary_types_allowed = True


class PutProfilePic(BaseModel):
    email: str
    first_name: str
    last_name: str
    permission: bool
    study_year: int
    pwd: str
    photo: Optional[bytes]
    reg_date: date

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class SwitchPermission(BaseModel):
    auth_code: str
    permission: bool

    class Config:
        orm_mode = True
