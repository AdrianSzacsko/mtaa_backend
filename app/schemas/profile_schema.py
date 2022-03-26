from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class GetProfileId(BaseModel):
    id: int
    email: str
    name: str
    permission: bool
    comments: int
    reg_date: date
    study_year: int


class GetProfileIdPic(BaseModel):
    user_photo: bytes

    class Config:
        arbitrary_types_allowed = True


class PutProfilePic(BaseModel):
    photo: Optional[bytes]

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class SwitchPermission(BaseModel):
    auth_code: str
    permission: bool

    class Config:
        orm_mode = True
