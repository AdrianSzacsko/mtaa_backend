from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ..schemas import prof_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from ..models import *
from ..security import auth

router = APIRouter(
    prefix="/prof",
    tags=["Prof"]
)


@router.get("/", response_model=List[prof_schema.GetProfId])
def get_prof(db: Session = Depends(create_connection),
             prof_id: Optional[int] = 0,
             user: User = Depends(auth.get_current_user)):
    result = db.query(Professor.id,
                      func.concat(Professor.first_name, " ", Professor.last_name).label("name"),
                      Subject.id.label("subj_id"),
                      Subject.name.label("subj_name"),
                      Subject.code.label("code"))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor with {prof_id} was not found."
        )

    join_query = result.join(Relation, Professor.id == Relation.prof_id) \
        .join(Subject, Relation.subj_id == Subject.id) \
        .filter(Professor.id == prof_id).all()

    return join_query


@router.get("/{prof_id}/reviews", response_model=List[prof_schema.GetProfId])
def get_prof_reviews(db: Session = Depends(create_connection),
                     prof_id: Optional[int] = 0,
                     user: User = Depends(auth.get_current_user)):
    result = db.query(Professor.id,
                      func.concat(Professor.first_name, " ", Professor.last_name).label("user_name"),
                      ProfessorReview.message,
                      ProfessorReview.rating,
                      User.id.label("user_id"))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with {prof_id} was not found."
        )

    join_query = result.join(ProfessorReview, Professor.id == ProfessorReview.prof_id) \
        .join(User, ProfessorReview.user_id == User.id) \
        .filter(Professor.id == prof_id).all()
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.post("/", status_code=HTTP_201_CREATED, response_model=prof_schema.PostProfId)
async def add_prof_review(prof: prof_schema.PostProfId,
                          db: Session = Depends(create_connection),
                          user: User = Depends(auth.get_current_user)):
    if len(prof.message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    prof_review = ProfessorReview(user_id=user.id, **prof.dict())

    db.add(prof_review)
    db.commit()
    db.refresh(prof_review)

    return prof_review


@router.put("/", status_code=HTTP_201_CREATED, response_model=prof_schema.PostProfId)
async def modify_prof_review(prof: prof_schema.PostProfId,
                             db: Session = Depends(create_connection),
                             user: User = Depends(auth.get_current_user)):
    if len(prof.message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    prof_review = ProfessorReview(**prof.dict())

    query = db.query(ProfessorReview).filter(and_(ProfessorReview.prof_id == prof_review.prof_id,
                                                  ProfessorReview.user_id == prof_review.user_id))

    query_row = query.first()
    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Review not found!",
        )

    if query_row.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized to perform this action."
        )

    query.update(prof.dict())
    db.commit()

    return prof_review
