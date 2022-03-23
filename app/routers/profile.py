from fastapi import APIRouter, Depends

from ..schemas import profile_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/", response_model=List[profile_schema.GetProfileId])
def get_profile(db: Session = Depends(create_connection), profile_id: Optional[int] = 0):
    result = db.query(User.id.label("user_id"),
                      User.email.label("user_email"),
                      func.concat(User.first_name, " ", User.last_name).label("user_name"),
                      User.permission.label("user_permission"),
                      User.comments.label("user_comments"),
                      User.reg_date.label("user_reg_date"),
                      User.study_year.label("user_study_year"))

    join_query = result.filter(User.id == profile_id).all()
    return join_query


@router.get("/{profile_id}/pic", response_model=List[profile_schema.GetProfileId])
def get_profile_pic(db: Session = Depends(create_connection), profile_id: Optional[int] = 0):
    result = db.query(User.photo.label("user_photo"))
    join_query = result.filter(User.id == profile_id).all()
    return join_query
