from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    first_name: str
    last_name: str
    study_year: int
    pwd: str


class PostRegister(BaseModel):
    email: str
    first_name: str
    last_name: str
    permission: bool
    study_year: int
    pwd: str

    class Config:
        orm_mode = True


class PostLogin(BaseModel):
    email: str
    pwd: str
