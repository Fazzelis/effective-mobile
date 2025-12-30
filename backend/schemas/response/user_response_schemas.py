from pydantic import BaseModel
from uuid import UUID
from schemas.internal.token_schemas import TokenInfoSchema
from schemas.internal.pagination_schemas import PaginationSchema


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


class UserChangedRoleResponseSchema(BaseModel):
    id: UUID
    name: str
    surname: str
    patronymic: str
    email: str
    role_name: str


class UserWithRoleNameResponseSchema(UserFullInfoSchema):
    role_name: str


class UsersResponseSchema(BaseModel):
    pagination: PaginationSchema
    users: list[UserWithRoleNameResponseSchema]
