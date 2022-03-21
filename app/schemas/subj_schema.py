from pydantic import BaseModel


class GetSubjectId(BaseModel):
    subj_name: str
    subj_code: str
    prof_first_name: str
    prof_last_name: str
    subj_r_message: str
    subj_r_difficulty: int
    subj_r_usability: int
    subj_r_prof_avg: int
    user_id: int
    user_first_name: str
    user_last_name: str


class PostSubjectId(BaseModel):
    subj_r_message: str
    subj_r_difficulty: int
    subj_r_usability: int
    subj_r_prof_avg: int


class PutSubjectId(BaseModel):
    subj_r_message: str
    subj_r_difficulty: int
    subj_r_usability: int
    subj_r_prof_avg: int