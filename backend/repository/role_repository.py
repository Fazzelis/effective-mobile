from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func
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

    async def get_all(self, page: int, page_size: int):
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Role)
            .offset(offset)
            .limit(page_size)
        )
        roles = result.scalars().all()
        count_result = await self.db.execute(select(func.count(Role.id)))
        total_count = count_result.scalar_one()
        return roles, total_count

    async def patch(
            self,
            role: Role,
            name: Optional[str] = None,
            read_posts_access: Optional[bool] = None,
            write_posts_access: Optional[bool] = None,
            delete_posts_access: Optional[bool] = None,
            manage_roles_access: Optional[bool] = None
    ) -> Role:
        if name is not None:
            role.name = name
        if read_posts_access is not None:
            role.read_posts_access = read_posts_access
        if write_posts_access is not None:
            role.write_posts_access = write_posts_access
        if delete_posts_access is not None:
            role.delete_posts_access = delete_posts_access
        if manage_roles_access is not None:
            role.manage_roles_access = manage_roles_access

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role
