from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import LargeBinary


class GetMyProfileId(BaseModel):
    user_id: int
    user_email: str
    user_first_name: str
    user_last_name: str
    user_permission: bool
    user_comments: int
    user_reg_date: datetime
    user_study_year: int


class GetMyProfileIdPic(BaseModel):
    user_photo: LargeBinary


class PostMyProfileIdPic(BaseModel):
    user_photo: LargeBinary


#TODO delete????