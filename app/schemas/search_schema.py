from pydantic import BaseModel


class GetSearch(BaseModel):
    subj_name: str
    subj_code: str
    prof_first_name: str
    prof_last_name: str