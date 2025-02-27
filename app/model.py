from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    email: EmailStr
    hashed_password: str
    libraries: List[str] = []