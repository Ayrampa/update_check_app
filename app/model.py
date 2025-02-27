from pydantic import BaseModel, EmailStr
from typing import List

class User(BaseModel):
    email: EmailStr
    libraries: List[str]