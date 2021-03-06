from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, \
    HTTP_403_FORBIDDEN

from .profile import increment_comment, decrement_comment
from ..schemas import prof_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from ..models import *
from ..security import auth

router = APIRouter(
    prefix="/prof",
    tags=["Professors"],
    responses={401: {"description": "Not authorized to perform this action."}}
)


@router.get("/{prof_id}", response_model=List[prof_schema.GetProfId], status_code=HTTP_200_OK,
            summary="Retrieves professor's profile.",
            responses={404: {"description": "Professor was not found."}})
def get_prof(db: Session = Depends(create_connection),
             prof_id: Optional[int] = 0,
             user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **prof_id**: professor's id

        Response values:

        - **id**: primary key representing professor
        - **name**: professor's full name
        - **subj_id**: id of a subject, that the professor teaches
        - **subj_name**: full name according to the subj_id
        - **code**: short form of the subj_name, typically an acronym
    """

    result = db.query(Professor.id,
                      func.concat(Professor.first_name, " ", Professor.last_name).label("name"),
                      Subject.id.label("subj_id"),
                      Subject.name.label("subj_name"),
                      Subject.code.label("code"))

    join_query = result.join(Relation, Professor.id == Relation.prof_id) \
        .join(Subject, Relation.subj_id == Subject.id) \
        .filter(Professor.id == prof_id).all()  # queried result needs to be joined accordingly

    if len(join_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor was not found."
        )

    return join_query


@router.get("/{prof_id}/reviews", response_model=List[prof_schema.GetProfIdReviews], status_code=HTTP_200_OK,
            summary="Retrieves reviews for specific professor.",
            responses={404: {"description": "Professor review was not found."}})
def get_prof_reviews(db: Session = Depends(create_connection),
                     prof_id: Optional[int] = 0,
                     user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **prof_id**: professor's id

        Response values:
        - **id**: primary key representing professor
        - **message**: text of the review itself
        - **rating**: numerical evaluation of the professor
        - **user_id**: author of the review
        - **user_name**: full name of the author
    """

    result = db.query(Professor.id,
                      func.concat(Professor.first_name, " ", Professor.last_name).label("user_name"),
                      ProfessorReview.message,
                      ProfessorReview.rating,
                      User.id.label("user_id"))

    join_query = result.join(ProfessorReview, Professor.id == ProfessorReview.prof_id) \
        .join(User, ProfessorReview.user_id == User.id) \
        .filter(Professor.id == prof_id).all()

    if len(join_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Professor review was not found."
        )
    # result = db.query(Subject).filter(Subject.id == {subj_id}).all()
    return join_query


def interval_exception(prof: prof_schema.PostProfId):
    """
    This method monitors various interval conditions that need to be met for correct front-end implementation
    """
    if len(prof.message) <= 2:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Review is too short.",
        )

    if not 0 <= prof.rating <= 100:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Rating is out of interval.",
        )


@router.post("/", status_code=HTTP_201_CREATED, response_model=prof_schema.PostProfIdOut,
             summary="Adds a review.",
             responses={404: {"description": "Professor was not found."},
                        403: {"description": "Interval is out of range."}})
async def add_prof_review(prof: prof_schema.PostProfId,
                          db: Session = Depends(create_connection),
                          user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **message**: textual form of the review
        - **rating**: numerical value representing review
        - **prof_id**: id of the reviewed professor

        Response values:

        - **message**: textual form of the review
        - **rating**: numerical value representing review
        - **user_id**: author's id, taken from token
        - **prof_id**: id of the reviewed professor
    """
    interval_exception(prof)

    query = db.query(ProfessorReview).filter(and_(ProfessorReview.prof_id == prof.prof_id,
                                                  ProfessorReview.user_id == user.id))
    query_row = query.first()  # retrieve only first result
    if query_row is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Review already exists, modify your existing one.",
        )

    if len(db.query(Professor).filter(Professor.id == prof.prof_id).all()) == 0:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Professor was not found.",
        )

    prof_review = ProfessorReview(user_id=user.id, **prof.dict())

    db.add(prof_review)  # 3 essential methods that post new values into database
    db.commit()
    db.refresh(prof_review)

    increment_comment(db, user)

    return prof_review


@router.put("/", status_code=HTTP_200_OK, response_model=prof_schema.PostProfIdOut,
            summary="Modifies a review.",
            responses={404: {"description": "Review was not found."},
                       403: {"description": "Interval is out of range."}})
async def modify_prof_review(prof: prof_schema.PostProfId,
                             db: Session = Depends(create_connection),
                             user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **message**: textual form of the review
        - **rating**: numerical value representing review
        - **prof_id**: id of the reviewed professor

        Response values:

        - **message**: textual form of the review
        - **rating**: numerical value representing review
        - **user_id**: author's id
        - **prof_id**: id of the reviewed professor
    """

    interval_exception(prof)

    prof_review = ProfessorReview(user_id=user.id, **prof.dict())

    query = db.query(ProfessorReview).filter(and_(ProfessorReview.prof_id == prof_review.prof_id,
                                                  ProfessorReview.user_id == user.id))

    query_row = query.first()
    if not query_row:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Review was not found.",
        )

    if query_row.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to perform this action."
        )

    updated_review = prof_schema.PostProfIdOut(user_id=user.id, **prof.dict())
    query.update(updated_review.dict())
    db.commit()

    return prof_review


@router.delete("/delete_review", status_code=HTTP_200_OK,
               summary="Deletes user review.",
               responses={404: {"description": "Review was not found."}})
def delete_review(uid: int, pid: int,
                  db: Session = Depends(create_connection),
                  user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **uid**: id of the author
        - **pid**: id of the reviewed professor
    """
    query = db.query(ProfessorReview).filter(and_(ProfessorReview.user_id == uid,
                                                  ProfessorReview.prof_id == pid))
    current_review = query.first()

    if uid != user.id and user.permission is False:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Permission denied.",
        )

    if current_review is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Review was not found.",
        )
    decrement_comment(db, user)

    db.delete(current_review)
    db.commit()
