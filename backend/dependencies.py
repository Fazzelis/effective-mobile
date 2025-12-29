from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.user_service import UserService
from services.role_service import RoleService


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db=db)


async def get_role_service(db: AsyncSession = Depends(get_db)):
    return RoleService(db=db)
