from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr
    
# Pydantic Model for Updating User Libraries
class UpdateLibraries(BaseModel):
    libraries: list[str]