from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from repository.role_repository import RoleRepository
from schemas.request.user_request_schemas import UserRegistrationRequestSchema, UserLoginRequestSchema, UserPatchRequestSchema
from schemas.response.user_response_schemas import UserInfoSchema, UserLogoutSchema, UserChangedRoleResponseSchema
from fastapi import Response, HTTPException, status
from schemas.response.user_response_schemas import UserAuthSchema, UserFullInfoSchema, UsersResponseSchema, UserWithRoleNameResponseSchema
from schemas.internal.token_schemas import TokenInfoSchema
from schemas.internal.pagination_schemas import PaginationSchema
from utils.jwt_utils import generate_token, decode_jwt
from configuration import settings
from utils.hasher import get_hash, match_hash
from jwt import ExpiredSignatureError
from schemas.request.user_request_schemas import UserChangeRoleRequestSchema


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repository: UserRepository = UserRepository(db=db)
        self.role_repository: RoleRepository = RoleRepository(db=db)

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
        role = await self.role_repository.get_by_name(name="user")
        user = await self.user_repository.post(
            name=payload.name,
            surname=payload.surname,
            patronymic=payload.patronymic,
            email=payload.email,
            password=get_hash(item=payload.password),
            role_id=role.id
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

    async def get_all(self, encoded_jwt: str | None, page: int, page_size: int) -> UsersResponseSchema:
        if encoded_jwt is None:
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
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.manage_roles_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )

            users, total_count = await self.user_repository.get_all(page=page, page_size=page_size)
            users_response = []
            for user in users:
                users_response.append(UserWithRoleNameResponseSchema(
                    id=user.id,
                    name=user.name,
                    surname=user.surname,
                    patronymic=user.patronymic,
                    email=user.email,
                    role_name=user.role.name
                ))
            return UsersResponseSchema(
                pagination=PaginationSchema(
                    page=page,
                    page_size=page_size,
                    total_count=total_count,
                    total_pages=(total_count + page_size - 1) // page_size
                ),
                users=users_response
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def change_role(
            self,
            payload: UserChangeRoleRequestSchema,
            encoded_jwt: str | None
    ) -> UserChangedRoleResponseSchema:
        if encoded_jwt is None:
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
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.manage_roles_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )

            user_for_edit = await self.user_repository.get_by_id(id=payload.user_id)
            if not user_for_edit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            role = await self.role_repository.get_by_id(id=payload.role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Роль не найдена"
                )
            edited_user = await self.user_repository.change_role(user=user_for_edit, role_id=payload.role_id)

            return UserChangedRoleResponseSchema(
                id=edited_user.id,
                name=edited_user.name,
                surname=edited_user.surname,
                patronymic=edited_user.patronymic,
                email=edited_user.email,
                role_name=role.name
            )

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
