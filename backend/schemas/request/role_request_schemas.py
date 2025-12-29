from pydantic import BaseModel
from schemas.internal.role_rights_schemas import RoleRightsSchema


class RoleRequestSchema(BaseModel):
    name: str
    role_rights: RoleRightsSchema
