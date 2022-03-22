from pydantic import BaseModel


class PostRegister(BaseModel):
    user_email: str
    user_first_name: str
    user_last_name: str
    user_permission: bool
    user_study_year: int
    user_password: str


class PostLogin(BaseModel):
    user_email: str
    user_password: str
