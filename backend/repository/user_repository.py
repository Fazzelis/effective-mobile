from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.user import User
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import selectinload


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def post(
            self,
            name: str,
            surname: str,
            patronymic: str,
            email: str,
            password: str,
            role_id: UUID
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            patronymic=patronymic,
            email=email,
            password=password,
            role_id=role_id
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

    async def get_all(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(User)
            .offset(offset)
            .limit(page_size)
            .options(
                selectinload(User.role)
            )
        )
        users = result.scalars().all()

        count_result = await self.db.execute(select(func.count(User.id)))
        total_count = count_result.scalar_one()
        return users, total_count

    async def patch(
            self,
            user: User,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            patronymic: Optional[str] = None,
            is_active: Optional[bool] = None
    ) -> User:
        if name is not None:
            user.name = name
        if surname is not None:
            user.surname = surname
        if patronymic is not None:
            user.patronymic = patronymic

        if is_active is not None:
            user.is_active = is_active

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_role(self, user: User, role_id: UUID) -> User:
        user.role_id = role_id
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
