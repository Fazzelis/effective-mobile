from sqlalchemy.ext.asyncio import AsyncSession
from repository.role_repository import RoleRepository
from repository.user_repository import UserRepository
from schemas.request.role_request_schemas import RoleRequestSchema, RolePatchRequestSchema
from schemas.response.role_response_schemas import RoleResponseSchema, RolesResponseSchema
from schemas.internal.role_rights_schemas import RoleRightsSchema
from fastapi import HTTPException, status
from utils.jwt_utils import decode_jwt
from jwt import ExpiredSignatureError
from schemas.internal.pagination_schemas import PaginationSchema
from uuid import UUID


class RoleService:
    def __init__(self, db: AsyncSession):
        self.role_repository: RoleRepository = RoleRepository(db=db)
        self.user_repository: UserRepository = UserRepository(db=db)

    async def create(self, payload: RoleRequestSchema, encoded_jwt: str | None) -> RoleResponseSchema:
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
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.manage_roles_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            new_role = await self.role_repository.post(
                role_name=payload.name,
                read_posts_access=payload.role_rights.read_posts_access,
                write_posts_access=payload.role_rights.write_posts_access,
                delete_posts_access=payload.role_rights.delete_posts_access,
                manage_roles_access=payload.role_rights.manage_roles_access
            )

            return RoleResponseSchema(
                id=new_role.id,
                name=new_role.name,
                role_rights=RoleRightsSchema(
                    read_posts_access=new_role.read_posts_access,
                    write_posts_access=new_role.write_posts_access,
                    delete_posts_access=new_role.delete_posts_access,
                    manage_roles_access=new_role.manage_roles_access
                )
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def get_all_roles(
            self,
            encoded_jwt: str | None,
            page: int,
            page_size: int,
    ) -> RolesResponseSchema:
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
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.manage_roles_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            roles, total_count = await self.role_repository.get_all(page=page, page_size=page_size)
            roles_response = []
            for role in roles:
                roles_response.append(RoleResponseSchema(
                    id=role.id,
                    name=role.name,
                    role_rights=RoleRightsSchema(
                        read_posts_access=role.read_posts_access,
                        write_posts_access=role.write_posts_access,
                        delete_posts_access=role.delete_posts_access,
                        manage_roles_access=role.manage_roles_access
                    )
                ))

            return RolesResponseSchema(
                pagination=PaginationSchema(
                    page=page,
                    page_size=page_size,
                    total_count=total_count,
                    total_pages=(total_count + page_size - 1) // page_size
                ),
                roles=roles_response
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )

    async def edit_role(
            self,
            role_id: UUID,
            payload: RolePatchRequestSchema,
            encoded_jwt: str | None
    ) -> RoleResponseSchema:
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
            user_role = await self.role_repository.get_by_id(id=user.role_id)
            if not user_role.manage_roles_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет прав"
                )
            role = await self.role_repository.get_by_id(id=role_id)
            edited_role = await self.role_repository.patch(
                role=role,
                name=payload.name,
                read_posts_access=payload.role_rights.read_posts_access,
                write_posts_access=payload.role_rights.write_posts_access,
                delete_posts_access=payload.role_rights.delete_posts_access,
                manage_roles_access=payload.role_rights.manage_roles_access
            )
            return RoleResponseSchema(
                id=edited_role.id,
                name=edited_role.name,
                role_rights=RoleRightsSchema(
                    read_posts_access=edited_role.read_posts_access,
                    write_posts_access=edited_role.write_posts_access,
                    delete_posts_access=edited_role.delete_posts_access,
                    manage_roles_access=edited_role.manage_roles_access
                )
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
