from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from models.role import Role
from typing import Optional


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def post(
            self,
            role_name: str,
            read_posts_access: Optional[bool] = True,
            write_posts_access: Optional[bool] = False,
            delete_posts_access: Optional[bool] = False,
            manage_roles_access: Optional[bool] = False
    ) -> Role:
        role = Role(
            name=role_name,
            read_posts_access=read_posts_access,
            write_posts_access=write_posts_access,
            delete_posts_access=delete_posts_access,
            manage_roles_access=manage_roles_access
        )
        self.db.add(role)

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_by_id(self, id: UUID) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.id == id))
        role = result.scalar_one_or_none()
        return role

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        return role
