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
    message: str
    rating: int
    prof_id: int

    class Config:
        orm_mode = True


class PostProfIdOut(BaseModel):
    message: str
    rating: int
    user_id: int
    prof_id: int

    class Config:
        orm_mode = True
