from pydantic import BaseModel
from schemas.internal.role_rights_schemas import RoleRightsSchema, RoleRightsPatchSchema
from typing import Optional


class RoleRequestSchema(BaseModel):
    name: str
    role_rights: RoleRightsSchema


class RolePatchRequestSchema(BaseModel):
    name: Optional[str] = None
    role_rights: Optional[RoleRightsPatchSchema]
