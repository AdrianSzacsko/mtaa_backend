from fastapi import APIRouter, Depends

from ..schemas import subj_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, union, select, or_, alias, text
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

    join_query = result.join(Relation, Subject.id == Relation.subj_id)\
        .join(Professor1, Relation.prof_id == Professor1.id)\
        .join(Professor2, Subject.prof_id == Professor2.id)\
        .filter(Subject.id == subj_id).all()
    #result = db.query(Subject).filter(Subject.id == {subj_id}).all()
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

    join_query = result.join(SubjectReview, Subject.id == SubjectReview.subj_id)\
        .join(User, SubjectReview.user_id == User.id)\
        .filter(Subject.id == subj_id).all()
    #result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query
