from pydantic import BaseModel


class GetProfId(BaseModel):
    id: int
    name: str
    subj_id: int
    subj_name: str
    code: str


class GetProfIdReviews(BaseModel):
    id: int
    message: str
    rating: int
    user_id: int
    user_name: str


class PostProfId(BaseModel):
    prof_review_table_message: str
    prof_review_table_rating: int
    user_id: int


class PutProfId(BaseModel):
    prof_review_table_message: str
    prof_review_table_rating: int
    user_id: int
