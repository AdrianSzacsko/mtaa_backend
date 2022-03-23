from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from ..schemas import subj_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *
from ..security import auth

router = APIRouter(
    prefix="/subj",
    tags=["Subj"]
)


def create_post_subject_id_to_db(subject: subj_schema.PostSubjectId, subj_id: int):
    post_subject_id_to_db = subj_schema.PostSubjectId_to_db(subj_id=subj_id,
                                                            user_id=subject.user_id,
                                                            message=subject.subj_r_message,
                                                            difficulty=subject.subj_r_difficulty,
                                                            prof_avg=subject.subj_r_prof_avg,
                                                            usability=subject.subj_r_usability)
    return post_subject_id_to_db


@router.get("/", response_model=List[subj_schema.GetSubjectId])
def get_subject_review(db: Session = Depends(create_connection),
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

    join_query = result.join(Relation, Subject.id == Relation.subj_id)\
        .join(Professor1, Relation.prof_id == Professor1.id)\
        .join(Professor2, Subject.prof_id == Professor2.id)\
        .filter(Subject.id == subj_id).all()
    #result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.get("/{subj_id}/reviews", response_model=List[subj_schema.GetSubjectIdReviews])
def get_subject(db: Session = Depends(create_connection),
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
            detail=f"Review with id:{subj_id} was not found."
        )

    join_query = result.join(SubjectReview, Subject.id == SubjectReview.subj_id)\
        .join(User, SubjectReview.user_id == User.id)\
        .filter(Subject.id == subj_id).all()
    #result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


@router.post("/", status_code=HTTP_201_CREATED, response_model=subj_schema.PostSubjectId_to_db)
async def register(subj: subj_schema.PostSubjectId,
                   db: Session = Depends(create_connection),
                   subj_id: Optional[int] = 0,
                   user: User = Depends(auth.get_current_user)):
    if len(subj.subj_r_message) <= 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message too short!",
        )

    post_subj_review = create_post_subject_id_to_db(subj, subj_id)

    subj_review = SubjectReview(**post_subj_review.dict())

    db.add(subj_review)
    db.commit()
    db.refresh(subj_review)

    return subj_review
