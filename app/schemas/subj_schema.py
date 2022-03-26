from pydantic import BaseModel


class GetSubjectId(BaseModel):
    id: int
    name: str
    teachers: str
    garant: str


class GetSubjectIdReviews(BaseModel):
    id: int
    message: str
    prof_avg: int
    usability: int
    difficulty: int
    user_name: str
    user_id: int


class PostSubjectId(BaseModel):
    message: str
    difficulty: int
    usability: int
    prof_avg: int
    subj_id: int

    class Config:
        orm_mode = True


class PostSubjectIdOut(BaseModel):
    message: str
    difficulty: int
    usability: int
    prof_avg: int
    user_id: int
    subj_id: int

    class Config:
        orm_mode = True
