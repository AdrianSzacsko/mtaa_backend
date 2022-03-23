from pydantic import BaseModel
from datetime import datetime


class GetProfileId(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    user_permission: bool
    user_comments: int
    user_reg_date: datetime
    user_study_year: int


class GetProfileIdPic(BaseModel):
    user_photo: bytearray

    class Config:
        arbitrary_types_allowed = True

