from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from schemas.request.role_request_schemas import RoleRequestSchema, RolePatchRequestSchema
from dependencies import get_role_service
from services.role_service import RoleService
from configuration import settings
from schemas.response.role_response_schemas import RoleResponseSchema, RolesResponseSchema
from uuid import UUID


router = APIRouter(
    prefix="/role",
    tags=["Role"]
)


@router.post("", response_model=RoleResponseSchema)
async def create(
        payload: RoleRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.create(payload=payload, encoded_jwt=credentials.credentials)


@router.get("", response_model=RolesResponseSchema)
async def get_all_roles(
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(5, ge=1, le=100, description="Количество элементов на странице"),
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.get_all_roles(encoded_jwt=credentials.credentials, page=page, page_size=page_size)


@router.patch("", response_model=RoleResponseSchema)
async def edit_rights(
        role_id: UUID,
        payload: RolePatchRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        role_service: RoleService = Depends(get_role_service)
):
    return await role_service.edit_role(role_id=role_id, payload=payload, encoded_jwt=credentials.credentials)
