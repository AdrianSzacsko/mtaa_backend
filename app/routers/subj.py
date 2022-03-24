from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ..schemas import subj_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text, and_
from typing import List, Optional
from ..models import *
from ..security import auth

router = APIRouter(
    prefix="/subj",
    tags=["Subj"]
)


@router.get("/", response_model=List[subj_schema.GetSubjectId])
def get_subject(db: Session = Depends(create_connection),
                subj_id: Optional[int] = 0,
                user: User = Depends(auth.get_current_user)):
    Professor1 = aliased(Professor)
    Professor2 = aliased(Professor)

    result = db.query(Subject.id, Subject.name,
                      func.concat(Professor1.first_name, " ", Professor1.last_name).label("teachers"),
                      func.concat(Professor2.first_name, " ", Professor2.last_name).label("garant"))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id:{subj_id} was not found."
        )

    join_query = result.join(Relation, Subject.id == Relation.subj_id) \
        .join(Professor1, Relation.prof_id == Professor1.id) \
        .join(Professor2, Subject.prof_id == Professor2.id) \
        .filter(Subject.id == subj_id).all()
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.get("/{subj_id}/reviews", response_model=List[subj_schema.GetSubjectIdReviews])
def get_subject_reviews(db: Session = Depends(create_connection),
                        subj_id: Optional[int] = 0,
                        user: User = Depends(auth.get_current_user)):
    result = db.query(Subject.id,
                      SubjectReview.message,
                      SubjectReview.prof_avg,
                      SubjectReview.usability,
                      SubjectReview.difficulty,
                      func.concat(User.first_name, " ", User.last_name).label("user_name"),
                      User.id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject review with id:{subj_id} was not found."
        )

    join_query = result.join(SubjectReview, Subject.id == SubjectReview.subj_id) \
        .join(User, SubjectReview.user_id == User.id) \
        .filter(Subject.id == subj_id).all()
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


def interval_exception(subj: subj_schema.PostSubjectId):
    if len(subj.message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    if not 0 <= subj.prof_avg <= 100:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Rating professor average out of interval!",
        )

    if not 0 <= subj.difficulty <= 100:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Rating difficulty out of interval!",
        )

    if not 0 <= subj.usability <= 100:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Rating usability out of interval!",
        )


@router.post("/", status_code=HTTP_201_CREATED, response_model=subj_schema.PostSubjectIdOut)
async def add_subj_review(subj: subj_schema.PostSubjectId,
                          db: Session = Depends(create_connection),
                          user: User = Depends(auth.get_current_user)):

    interval_exception(subj)

    query = db.query(SubjectReview).filter(and_(SubjectReview.subj_id == subj.subj_id,
                                                SubjectReview.user_id == user.id))
    if query.first() is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Review already exists, for modification use PUT!",
        )

    subj_review = SubjectReview(user_id=user.id, **subj.dict())

    db.add(subj_review)
    db.commit()
    db.refresh(subj_review)

    return subj_review


@router.put("/", status_code=HTTP_201_CREATED, response_model=subj_schema.PostSubjectIdOut)
async def modify_subj_review(subj: subj_schema.PostSubjectId,
                             db: Session = Depends(create_connection),
                             user: User = Depends(auth.get_current_user)):

    interval_exception(subj)

    subj_review = SubjectReview(user_id=user.id, **subj.dict())

    query = db.query(SubjectReview).filter(and_(SubjectReview.subj_id == subj_review.subj_id,
                                                SubjectReview.user_id == user.id))

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



    updated_review = subj_schema.PostSubjectIdOut(user_id=user.id, **subj.dict())
    query.update(updated_review.dict())
    query.update(subj.dict())
    db.commit()

    return subj_review
