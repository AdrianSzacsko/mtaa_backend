from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..schemas.auth_schema import Token
from ..db.database import create_connection
from ..settings import settings
from ..security import auth
from ..models import User

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)


@router.post("/", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(create_connection)):

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
