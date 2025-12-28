from pydantic import BaseModel, EmailStr


class UserRequestSchema(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    password: str
    repeat_password: str
