from fastapi import APIRouter, HTTPException, status, Depends
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from ..models import User
from ..schemas.register_login_schema import PostRegister
from sqlalchemy.orm import Session
from ..security.passwords import get_password_hash
from ..db.database import create_connection

router = APIRouter(
    prefix="/register",
    tags=["Register"]
)


@router.post("", status_code=HTTP_201_CREATED, response_model=PostRegister)
async def register(user: PostRegister, db: Session = Depends(create_connection)):
    user.password = get_password_hash(user.user_password)
    """
    if await check_email_is_taken(user.user_email):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Email already taken!",
        )
    """

    registered_user = User()
    db.add(registered_user)
    db.commit().refresh(registered_user)

    return registered_user
