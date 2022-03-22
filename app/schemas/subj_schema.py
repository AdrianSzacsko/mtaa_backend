from pydantic import BaseModel


class GetSubjectId(BaseModel):
    id: str
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
    subj_r_message: str
    subj_r_difficulty: int
    subj_r_usability: int
    subj_r_prof_avg: int
    user_id: int


class PutSubjectId(BaseModel):
    subj_r_message: str
    subj_r_difficulty: int
    subj_r_usability: int
    subj_r_prof_avg: int
    user_id: int