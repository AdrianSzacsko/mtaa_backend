from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import LargeBinary


class GetProfileId(BaseModel):
    id: int
    email: str
    name: str
    permission: bool
    comments: int
    reg_date: datetime
    study_year: int


class GetProfileIdPic(BaseModel):
    user_photo: bytearray

