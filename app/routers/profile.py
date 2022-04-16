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
from PIL import Image

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    responses={401: {"description": "Not authorized to perform this action."}}
)


def increment_comment(db: Session, user: User):
    user_query = db.query(User).filter(User.id == user.id)
    user_comment = user_query.first().comments
    user_query.update({"comments": user_comment + 1})
    db.commit()


def decrement_comment(db: Session, user: User):
    user_query = db.query(User).filter(User.id == user.id)
    user_comment = user_query.first().comments
    if user_comment > 0:
        user_query.update({"comments": user_comment - 1})
        db.commit()


@router.get("/{profile_id}", response_model=List[profile_schema.GetProfileId], status_code=HTTP_200_OK,
            summary="Retrieves user profile.",
            responses={404: {"description": "Profile was not found."}})
def get_profile(db: Session = Depends(create_connection),
                profile_id: Optional[int] = 0,
                user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **profile_id**: identifier of the user

        Response values:

        - **id**: unique identifier
        - **email**: unique email, also serves as username
        - **name**: user's real name
        - **permission**: whether admin permission is granted
        - **comments**: number of posted reviews
        - **reg_date**: registration date
        - **study_year**: current year of study
    """

    result = db.query(User.id.label("id"),
                      User.email.label("email"),
                      func.concat(User.first_name, " ", User.last_name).label("name"),
                      User.permission.label("permission"),
                      User.comments.label("comments"),
                      User.reg_date.label("reg_date"),
                      User.study_year.label("study_year"))

    filter_query = result.filter(User.id == profile_id).all()

    if len(filter_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile was not found."
        )
    return filter_query


@router.get("/{profile_id}/pic", status_code=HTTP_200_OK,
            summary="Retrieves user profile picture.",
            responses={404: {"description": "Profile picture was not found."}})
def get_profile_pic(db: Session = Depends(create_connection),
                    profile_id: Optional[int] = 0,
                    user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **profile_id**: id of the user

        Response values:
        - binary form of profile picture
    """

    result = db.query(User.photo.label("user_photo"))
    filter_query = result.filter(User.id == profile_id).first()

    if filter_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile was not found."
        )

    if filter_query[0] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile picture was not found."
        )
    # image_type = magic.from_buffer(filter_query[0], mime=True)
    image_type = Image.open(io.BytesIO(filter_query[0])).format.lower()
    return Response(content=filter_query[0], media_type=f'image/{image_type}')


def check_if_picture(file: UploadFile = File(...)):
    # check_filetype
    supported_files = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in supported_files:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported file type.",
        )
    file_bytes = file.file.read()
    size = len(file_bytes)
    if size > 3 * 1024 * 1024:  # 3MB = 3*1024 KB = 3* 1024 * 1024
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selected file is too large.",
        )
    return file_bytes


@router.put("/pic", status_code=HTTP_200_OK,
            summary="Posts new profile picture.",
            responses={404: {"description": "Profile was not found."},
                       422: {"description": "Unprocessable file."}})
async def add_profile_pic(file: UploadFile = File(...),
                          db: Session = Depends(create_connection),
                          user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    query_row = query.first()

    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile was not found.",
        )

    if query_row.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    file_bytes = check_if_picture(file)
    query.update({"photo": file_bytes})
    db.commit()
    return StreamingResponse(io.BytesIO(file_bytes), media_type=file.content_type)


@router.delete("/", status_code=HTTP_200_OK,
               summary="Deletes user profile.",
               responses={404: {"description": "Profile was not found"}})
def delete_user_profile(db: Session = Depends(create_connection),
                        user: User = Depends(auth.get_current_user)):
    query = db.query(User).filter(User.id == user.id)
    current_user = query.first()

    if current_user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile was not found.",
        )

    if current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    db.delete(current_user)
    db.commit()


@router.put("/delete_pic", status_code=HTTP_200_OK, response_model=profile_schema.PutProfilePic,
            summary="Deletes current profile picture. **This API call was marked as DELETE in first doc.**",
            responses={404: {"description": "Profile was not found"}})
def delete_profile_pic(db: Session = Depends(create_connection),
                       user: User = Depends(auth.get_current_user)):
    """
        Response values:

        - **photo**: empty photo value
    """

    query = db.query(User).filter(User.id == user.id)
    query_row = query.first()

    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Profile was not found.",
        )

    if query_row.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    query.update({"photo": None})
    db.commit()

    return {"photo": None}
