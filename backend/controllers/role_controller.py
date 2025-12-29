from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from schemas.request.role_request_schemas import RoleRequestSchema
from dependencies import get_role_service
from services.role_service import RoleService
from configuration import settings


router = APIRouter(
    prefix="/role",
    tags=["Role"]
)


@router.post("")
async def create(
        payload: RoleRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.create(payload=payload, encoded_jwt=credentials.credentials)
