from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    libraries: List[str]

class UserDB(UserCreate):
    id: str