from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from uuid import UUID
from typing import Optional


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def post(
            self,
            name: str,
            surname: str,
            patronymic: str,
            email: str,
            password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            patronymic=patronymic,
            email=email,
            password=password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user

    async def get_by_id(self, id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        user = result.scalar_one_or_none()
        return user

    async def patch(
            self,
            user: User,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            patronymic: Optional[str] = None,
            is_active: Optional[bool] = True
    ) -> User:
        if name:
            user.name = name
        if surname:
            user.surname = surname
        if patronymic:
            user.patronymic = patronymic

        user.is_active = is_active

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
