from fastapi import APIRouter, Depends, Response, Cookie
from schemas.request.user_request_schemas import UserRegistrationRequestSchema, UserLoginRequestSchema, UserPatchRequestSchema
from schemas.response.user_response_schemas import UserInfoSchema, UserLogoutSchema, UserFullInfoSchema
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
