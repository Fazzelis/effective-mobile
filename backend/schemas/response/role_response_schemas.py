from pydantic import BaseModel
from uuid import UUID
from schemas.internal.role_rights_schemas import RoleRightsSchema
from schemas.internal.pagination_schemas import PaginationSchema


class RoleResponseSchema(BaseModel):
    id: UUID
    name: str
    role_rights: RoleRightsSchema


class RolesResponseSchema(BaseModel):
    pagination: PaginationSchema
    roles: list[RoleResponseSchema]
