from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import LargeBinary


class GetProfileId(BaseModel):
    user_id: int
    user_email: str
    user_first_name: str
    user_last_name: str
    user_permission: bool
    user_comments: int
    user_reg_date: datetime
    user_study_year: int


class GetProfileIdPic(BaseModel):
    user_photo: LargeBinary

