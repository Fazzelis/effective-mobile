from sqlalchemy.ext.asyncio import AsyncSession
from repository.role_repository import RoleRepository
from repository.user_repository import UserRepository
from schemas.request.role_request_schemas import RoleRequestSchema
from schemas.response.role_response_schemas import RoleResponseSchema
from schemas.internal.role_rights_schemas import RoleRightsSchema
from fastapi import HTTPException, status
from utils.jwt_utils import decode_jwt
from jwt import ExpiredSignatureError


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
