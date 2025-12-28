from pydantic import BaseModel
from uuid import UUID
from schemas.internal.token_schemas import TokenInfoSchema


class UserAuthSchema(BaseModel):
    user_id: UUID
    token_info: TokenInfoSchema


class UserInfoSchema(BaseModel):
    id: UUID
    name: str
    surname: str
    patronymic: str


class UserFullInfoSchema(UserInfoSchema):
    email: str


class UserLogoutSchema(BaseModel):
    message: str
