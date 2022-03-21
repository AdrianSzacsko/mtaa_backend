from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str


class UserInDB(User):
    hashed_password: str
