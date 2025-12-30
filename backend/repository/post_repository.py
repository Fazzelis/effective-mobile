from sqlalchemy.ext.asyncio import AsyncSession
from models.post import Post
from uuid import UUID
from sqlalchemy import select, func, delete


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def post(self, title: str, text: str, author_id: UUID) -> Post:
        post = Post(
            title=title,
            text=text,
            author_id=author_id
        )
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_all(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Post)
            .offset(offset)
            .limit(page_size)
        )

        roles = result.scalars().all()
        count_result = await self.db.execute(select(func.count(Post.id)))
        total_count = count_result.scalar_one()
        return roles, total_count

    async def get_by_id(self, post_id: UUID) -> Post:
        result = await self.db.execute(
            select(Post)
            .where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()

        return post

    async def delete(self, post_id: UUID) -> int:
        result = await self.db.execute(
            delete(Post)
            .where(Post.id == post_id)
        )

        await self.db.commit()
        return result.rowcount
