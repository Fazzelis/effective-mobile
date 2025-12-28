from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from schemas.request.user_request_schemas import UserRequestSchema
from fastapi import Response, HTTPException, status
from schemas.response.user_response_schema import UserAuthSchema
from schemas.internal.token_schemas import TokenInfoSchema
from utils.jwt_utils import generate_token, decode_jwt
from configuration import settings


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository: UserRepository = UserRepository(db=db)

    async def create(
            self,
            payload: UserRequestSchema,
            response: Response
    ) -> UserAuthSchema:
        if payload.password != payload.repeat_password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пароли не совпадают"
            )
        optional_user = await self.user_repository.get_by_email(email=payload.email)
        if optional_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с такой почтой уже существует"
            )
        user = await self.user_repository.post(
            name=payload.name,
            surname=payload.surname,
            patronymic=payload.patronymic,
            email=payload.email,
            password=payload.password
        )

        access_token = generate_token(user_id=user.id, token_type="access")
        refresh_token = generate_token(user_id=user.id, token_type="refresh")

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=settings.expiration_time_of_refresh_token_for_browser
        )

        return UserAuthSchema(
            user_id=user.id,
            token_info=TokenInfoSchema(
                token=access_token,
                token_type="Bearer"
            )
        )
