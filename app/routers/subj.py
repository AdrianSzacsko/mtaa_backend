from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ..schemas import subj_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text, and_
from typing import List, Optional
from ..models import *

router = APIRouter(
    prefix="/subj",
    tags=["Subj"]
)


@router.get("/", response_model=List[subj_schema.GetSubjectId])
def get_subject(db: Session = Depends(create_connection), subj_id: Optional[int] = 0):
    Professor1 = aliased(Professor)
    Professor2 = aliased(Professor)

    result = db.query(Subject.id, Subject.name,
                      func.concat(Professor1.first_name, " ", Professor1.last_name).label("teachers"),
                      func.concat(Professor2.first_name, " ", Professor2.last_name).label("garant"))

    join_query = result.join(Relation, Subject.id == Relation.subj_id) \
        .join(Professor1, Relation.prof_id == Professor1.id) \
        .join(Professor2, Subject.prof_id == Professor2.id) \
        .filter(Subject.id == subj_id).all()
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.get("/{subj_id}/reviews", response_model=List[subj_schema.GetSubjectIdReviews])
def get_subject(db: Session = Depends(create_connection), subj_id: Optional[int] = 0):
    result = db.query(Subject.id,
                      SubjectReview.message,
                      SubjectReview.prof_avg,
                      SubjectReview.usability,
                      SubjectReview.difficulty,
                      func.concat(User.first_name, " ", User.last_name).label("user_name"),
                      User.id)

    join_query = result.join(SubjectReview, Subject.id == SubjectReview.subj_id) \
        .join(User, SubjectReview.user_id == User.id) \
        .filter(Subject.id == subj_id).all()
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.post("/", status_code=HTTP_201_CREATED, response_model=subj_schema.PostSubjectId)
async def add_subj_review(subj: subj_schema.PostSubjectId, db: Session = Depends(create_connection)):
    if len(subj.message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    subj_review = SubjectReview(**subj.dict())

    db.add(subj_review)
    db.commit()
    db.refresh(subj_review)

    return subj_review


@router.put("/", status_code=HTTP_201_CREATED, response_model=subj_schema.PostSubjectId)
async def modify_subj_review(subj: subj_schema.PostSubjectId, db: Session = Depends(create_connection)):
    if len(subj.message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    subj_review = SubjectReview(**subj.dict())

    query = db.query(SubjectReview).filter(and_(SubjectReview.subj_id == subj_review.subj_id,
                                                SubjectReview.user_id == subj_review.user_id))

    query_row = query.first()
    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Review not found!",
        )
    query.update(subj.dict())
    db.commit()

    return subj_review
