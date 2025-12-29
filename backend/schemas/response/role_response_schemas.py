from pydantic import BaseModel
from uuid import UUID
from schemas.internal.role_rights_schemas import RoleRightsSchema


class RoleResponseSchema(BaseModel):
    id: UUID
    name: str
    role_rights: RoleRightsSchema
