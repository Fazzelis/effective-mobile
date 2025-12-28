from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from schemas.request.user_request_schemas import UserRegistrationRequestSchema, UserLoginRequestSchema, UserPatchRequestSchema
from schemas.response.user_response_schema import UserInfoSchema, UserLogoutSchema
from fastapi import Response, HTTPException, status
from schemas.response.user_response_schema import UserAuthSchema, UserFullInfoSchema
from schemas.internal.token_schemas import TokenInfoSchema
from utils.jwt_utils import generate_token, decode_jwt
from configuration import settings
from utils.hasher import get_hash, match_hash
from jwt import ExpiredSignatureError


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository: UserRepository = UserRepository(db=db)

    async def create(
            self,
            payload: UserRegistrationRequestSchema,
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
            password=get_hash(item=payload.password)
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

    async def login(
            self,
            payload: UserLoginRequestSchema,
            response: Response
    ) -> UserAuthSchema:
        user = await self.user_repository.get_by_email(email=payload.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Неправильный логин или пароль"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Неправильный логин или пароль"
            )
        if not match_hash(item=payload.password, item_hash=user.password):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Неправильный логин или пароль"
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

    async def update(
            self,
            payload: UserPatchRequestSchema,
            encoded_jwt: str | None
    ) -> UserInfoSchema:
        if not encoded_jwt:
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
            updated_user = await self.user_repository.patch(
                user=user,
                name=payload.name,
                surname=payload.surname,
                patronymic=payload.patronymic
            )
            return UserInfoSchema(
                id=updated_user.id,
                name=updated_user.name,
                surname=updated_user.surname,
                patronymic=updated_user.patronymic
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def refresh_token(self, refresh_token: str | None, response: Response):
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token не найден"
            )
        try:
            user_id = decode_jwt(token=refresh_token)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
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

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def logout(self, response: Response):
        response.delete_cookie(key="refresh_token", secure=True, samesite="none", httponly=True)
        return UserLogoutSchema(
            message="Refresh token был удален"
        )

    async def delete(self, encoded_jwt: str | None, response: Response, refresh_token: str | None):
        if not encoded_jwt or not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не найден токен"
            )
        try:
            user_id = decode_jwt(token=encoded_jwt)
            user = await self.user_repository.get_by_id(id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )

            await self.user_repository.patch(user=user, is_active=False)
            response.delete_cookie(key="refresh_token", secure=True, samesite="none", httponly=True)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def get_profile(self, encoded_jwt: str | None) -> UserFullInfoSchema:
        if not encoded_jwt:
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
            return UserFullInfoSchema(
                id=user.id,
                name=user.name,
                surname=user.surname,
                patronymic=user.patronymic,
                email=user.email
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
