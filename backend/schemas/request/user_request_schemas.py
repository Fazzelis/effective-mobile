from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegistrationRequestSchema(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    password: str
    repeat_password: str


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserPatchRequestSchema(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
