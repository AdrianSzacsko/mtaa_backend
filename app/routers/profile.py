from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK

from ..schemas import profile_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *
from ..security import auth

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/", response_model=List[profile_schema.GetProfileId])
def get_profile(db: Session = Depends(create_connection),
                profile_id: Optional[int] = 0,
                user: User = Depends(auth.get_current_user)):
    result = db.query(User.id.label("user_id"),
                      User.email.label("user_email"),
                      func.concat(User.first_name, " ", User.last_name).label("user_name"),
                      User.permission.label("user_permission"),
                      User.comments.label("user_comments"),
                      User.reg_date.label("user_reg_date"),
                      User.study_year.label("user_study_year"))

    filter_query = result.filter(User.id == profile_id).all()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with {profile_id} was not found."
        )
    return filter_query


@router.get("/{profile_id}/pic", response_model=List[profile_schema.GetProfileId])
def get_profile_pic(db: Session = Depends(create_connection),
                    profile_id: Optional[int] = 0,
                    user: User = Depends(auth.get_current_user)):
    result = db.query(User.photo.label("user_photo"))
    filter_query = result.filter(User.id == profile_id).all()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile picture related to id {profile_id} was not found."
        )

    return filter_query


@router.put("/pic", status_code=HTTP_201_CREATED, response_model=profile_schema.PutProfilePic)
async def add_profile_pic(profile: profile_schema.GetProfileIdPic,
                          db: Session = Depends(create_connection),
                          user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    query_row = query.first()

    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile not found!",
        )

    if query_row.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to perform this action."
        )

    updated_profile_pic = profile_schema.PutProfilePic(
        email=query_row.email,
        first_name=query_row.first_name,
        last_name=query_row.last_name,
        permission=query_row.permission,
        study_year=query_row.study_year,
        pwd=query_row.pwd,
        photo=profile.user_photo,
        reg_date=query_row.reg_date
    )

    query.update(updated_profile_pic.dict())
    db.commit()

    return updated_profile_pic.dict()


@router.put("/admin", status_code=HTTP_201_CREATED, response_model=profile_schema.SwitchPermission)
async def switch_admin_permission(profile: profile_schema.SwitchPermission,
                                  db: Session = Depends(create_connection),
                                  user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    query_row = query.first()

    if profile.auth_code != "admin1234":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Permission denied!"
        )

    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile not found!",
        )

    query.update({"permission": profile.permission})
    db.commit()
    profile.auth_code = "****"
    return profile.dict()


@router.delete("/", status_code=HTTP_200_OK)
def delete_user_profile(db: Session = Depends(create_connection),
                        user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    current_user = query.first()

    if current_user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile not found!",
        )

    if current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to perform this action."
        )

    db.delete(current_user)
    db.commit()


@router.put("/delete_pic", status_code=HTTP_200_OK, response_model=profile_schema.PutProfilePic)
def delete_profile_pic(db: Session = Depends(create_connection),
                       user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    query_row = query.first()

    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile not found!",
        )

    if query_row.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to perform this action."
        )

    updated_profile_pic = profile_schema.PutProfilePic(
        email=query_row.email,
        first_name=query_row.first_name,
        last_name=query_row.last_name,
        permission=query_row.permission,
        study_year=query_row.study_year,
        pwd=query_row.pwd,
        reg_date=query_row.reg_date
    )

    query.update(updated_profile_pic.dict())
    db.commit()

    return updated_profile_pic.dict()
