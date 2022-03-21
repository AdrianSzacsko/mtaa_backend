from pydantic import BaseModel


class GetProfId(BaseModel):
    prof_first_name: str
    prof_last_name: str
    subj_name: str
    prof_review_table_message: str
    prof_review_table_rating: int
    user_table_id: int
    user_table_first_name: str
    user_table_last_name: str


class PostProfId(BaseModel):
    prof_review_table_message: str
    prof_review_table_rating: int


class PutProfId(BaseModel):
    prof_review_table_message: str
    prof_review_table_rating: int