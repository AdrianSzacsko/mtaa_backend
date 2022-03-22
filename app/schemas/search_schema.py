from pydantic import BaseModel


class GetSearch(BaseModel):
    name: str
    code: str
    id: int
