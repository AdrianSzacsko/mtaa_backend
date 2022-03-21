from fastapi import APIRouter

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)