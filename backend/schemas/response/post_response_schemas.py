from pydantic import BaseModel
from uuid import UUID
from schemas.internal.pagination_schemas import PaginationSchema


class PostResponseSchema(BaseModel):
    id: UUID
    title: str
    text: str


class PostsResponseSchema(BaseModel):
    pagination: PaginationSchema
    posts: list[PostResponseSchema]
