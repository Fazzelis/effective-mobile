from fastapi import APIRouter, Depends, Response
from schemas.request.user_request_schemas import UserRequestSchema
from dependencies import get_user_service
from services.user_service import UserService


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("")
async def registration(
        payload: UserRequestSchema,
        response: Response,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create(payload=payload, response=response)
