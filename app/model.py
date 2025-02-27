# from pydantic import BaseModel, EmailStr
# from typing import List

# class User(BaseModel):
#     email: EmailStr
#     hashed_password: str
#     libraries: List[str] = []
from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserDB(BaseModel):
    email: EmailStr
    hashed_password: str
    libraries: List[str] = []
