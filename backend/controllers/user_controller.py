from fastapi import APIRouter, Depends, Response, Cookie, Query
from schemas.request.user_request_schemas import UserRegistrationRequestSchema, UserLoginRequestSchema
from schemas.request.user_request_schemas import UserPatchRequestSchema, UserChangeRoleRequestSchema
from schemas.response.user_response_schemas import UserInfoSchema, UserLogoutSchema, UserFullInfoSchema
from schemas.response.user_response_schemas import UserChangedRoleResponseSchema
from dependencies import get_user_service
from services.user_service import UserService
from schemas.response.user_response_schemas import UserAuthSchema
from fastapi.security import HTTPAuthorizationCredentials
from configuration import settings


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/registration", response_model=UserAuthSchema)
async def registration(
        payload: UserRegistrationRequestSchema,
        response: Response,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create(payload=payload, response=response)


@router.post("/login", response_model=UserAuthSchema)
async def login(
        payload: UserLoginRequestSchema,
        response: Response,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.login(payload=payload, response=response)


@router.patch("/update", response_model=UserInfoSchema)
async def update(
        payload: UserPatchRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.update(payload=payload, encoded_jwt=credentials.credentials)


@router.post("/refresh")
async def refresh_tokens(
        response: Response,
        refresh_token: str | None = Cookie(default=None),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.refresh_token(refresh_token=refresh_token, response=response)


@router.get("", response_model=UserLogoutSchema)
async def logout(
        response: Response,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.logout(response=response)


@router.patch("/delete")
async def delete(
        response: Response,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        refresh_token: str | None = Cookie(default=None),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.delete(encoded_jwt=credentials.credentials, response=response, refresh_token=refresh_token)


@router.get("/profile")
async def get_profile(
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        user_service: UserService = Depends(get_user_service)
) -> UserFullInfoSchema:
    return await user_service.get_profile(encoded_jwt=credentials.credentials)


@router.get("/all")
async def get_all(
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        page_size: int = Query(default=5, ge=1, le=100, description="Количество элементов на странице"),
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_all(encoded_jwt=credentials.credentials, page=page, page_size=page_size)


@router.patch("/change-role", response_model=UserChangedRoleResponseSchema)
async def change_role(
        payload: UserChangeRoleRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.change_role(payload=payload, encoded_jwt=credentials.credentials)
