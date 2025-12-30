from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials
from configuration import settings
from schemas.request.post_request_schemas import PostRequestSchema
from schemas.response.post_response_schemas import PostResponseSchema, PostsResponseSchema
from schemas.response.item_delete_response_schemas import ItemDeleteResponse
from dependencies import get_post_service
from services.post_service import PostService
from uuid import UUID


router = APIRouter(
    prefix="/post",
    tags=["Post"]
)


@router.post("", response_model=PostResponseSchema)
async def create(
        payload: PostRequestSchema,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        post_service: PostService = Depends(get_post_service)
):
    return await post_service.create(payload=payload, encoded_jwt=credentials.credentials)


@router.get("/all", response_model=PostsResponseSchema)
async def get_all(
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        page_size: int = Query(default=5, ge=1, le=100, description="Количество элементов на странице"),
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        post_service: PostService = Depends(get_post_service)
):
    return await post_service.get_all(encoded_jwt=credentials.credentials, page=page, page_size=page_size)


@router.get("", response_model=PostResponseSchema)
async def get(
        post_id: UUID,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        post_service: PostService = Depends(get_post_service)
):
    return await post_service.get(post_id=post_id, encoded_jwt=credentials.credentials)


@router.delete("", response_model=ItemDeleteResponse)
async def delete(
        post_id: UUID,
        credentials: HTTPAuthorizationCredentials = Depends(settings.http_bearer),
        post_service: PostService = Depends(get_post_service)
):
    return await post_service.delete(encoded_jwt=credentials.credentials, post_id=post_id)
