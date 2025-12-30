from sqlalchemy.ext.asyncio import AsyncSession
from repository.post_repository import PostRepository
from repository.user_repository import UserRepository
from repository.role_repository import RoleRepository
from fastapi import HTTPException, status
from schemas.request.post_request_schemas import PostRequestSchema
from schemas.response.post_response_schemas import PostResponseSchema, PostsResponseSchema
from schemas.response.item_delete_response_schemas import ItemDeleteResponse
from schemas.internal.pagination_schemas import PaginationSchema
from utils.jwt_utils import decode_jwt
from jwt import ExpiredSignatureError
from uuid import UUID


class PostService:
    def __init__(self, db: AsyncSession):
        self.post_repository: PostRepository = PostRepository(db=db)
        self.user_repository: UserRepository = UserRepository(db=db)
        self.role_repository: RoleRepository = RoleRepository(db=db)

    async def create(self, payload: PostRequestSchema, encoded_jwt: str | None) -> PostResponseSchema:
        if encoded_jwt is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не найден"
            )
        try:
            user_id = decode_jwt(token=encoded_jwt)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.write_posts_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            post = await self.post_repository.post(title=payload.title, text=payload.text, author_id=user.id)

            return PostResponseSchema(
                id=post.id,
                title=post.title,
                text=post.text
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def get_all(self, encoded_jwt: str | None, page: int, page_size: int):
        if encoded_jwt is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не найден"
            )
        try:
            user_id = decode_jwt(token=encoded_jwt)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.read_posts_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            posts, total_count = await self.post_repository.get_all(page=page, page_size=page_size)

            posts_response = []
            for post in posts:
                posts_response.append(PostResponseSchema(
                    id=post.id,
                    title=post.title,
                    text=post.text
                ))

            return PostsResponseSchema(
                pagination=PaginationSchema(
                    page=page,
                    page_size=page_size,
                    total_count=total_count,
                    total_pages=(total_count + page_size - 1) // page_size
                ),
                posts=posts_response
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def get(self, post_id: UUID, encoded_jwt: str | None):
        if encoded_jwt is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не найден"
            )
        try:
            user_id = decode_jwt(token=encoded_jwt)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.read_posts_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            post = await self.post_repository.get_by_id(post_id=post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не найден"
                )

            return PostResponseSchema(
                id=post.id,
                title=post.title,
                text=post.text
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def delete(self, encoded_jwt: str | None, post_id: UUID) -> ItemDeleteResponse:
        if encoded_jwt is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не найден"
            )
        try:
            user_id = decode_jwt(token=encoded_jwt)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.delete_posts_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            row_count = await self.post_repository.delete(post_id=post_id)
            return ItemDeleteResponse(
                item_id=post_id,
                row_count=row_count
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
