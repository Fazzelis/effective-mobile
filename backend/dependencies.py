from fastapi import Depends
from services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db=db)
