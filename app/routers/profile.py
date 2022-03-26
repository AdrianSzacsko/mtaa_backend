from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY
from starlette.responses import StreamingResponse, Response

from ..schemas import profile_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *
from ..security import auth
import io
import magic

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


def increment_comment(db: Session, user: User):
    user_query = db.query(User).filter(User.id == user.id)
    user_comment = user_query.first().comments
    user_query.update({"comments": user_comment + 1})
    db.commit()


@router.get("/", response_model=List[profile_schema.GetProfileId], status_code=HTTP_200_OK)
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

    if len(filter_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with {profile_id} was not found."
        )
    return filter_query


@router.get("/{profile_id}/pic", status_code=HTTP_200_OK)
def get_profile_pic(db: Session = Depends(create_connection),
                    profile_id: Optional[int] = 0,
                    user: User = Depends(auth.get_current_user)):
    result = db.query(User.photo.label("user_photo"))
    filter_query = result.filter(User.id == profile_id).first()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile related to id {profile_id} was not found."
        )

    if filter_query[0] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile picture related to id {profile_id} was not found."
        )
    image_type = magic.from_buffer(filter_query[0], mime=True)
    return Response(content=filter_query[0], media_type=image_type)


def check_if_picture(file: UploadFile = File(...)):
    # check_filetype
    supported_files = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in supported_files:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type!",
        )
    file_bytes = file.file.read()
    size = len(file_bytes)
    if size > 3 * 1024 * 1024: #3MB = 3*1024 KB = 3* 1024 * 1024
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File too large",
        )
    return file_bytes


@router.put("/pic", status_code=HTTP_200_OK)
async def add_profile_pic(file: UploadFile = File(...),
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

    file_bytes = check_if_picture(file)
    query.update({"photo": file_bytes})
    db.commit()
    return StreamingResponse(io.BytesIO(file_bytes), media_type=file.content_type)


@router.put("/admin", status_code=HTTP_200_OK, response_model=profile_schema.SwitchPermission)
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
