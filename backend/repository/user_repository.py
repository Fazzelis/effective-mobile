from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User


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
