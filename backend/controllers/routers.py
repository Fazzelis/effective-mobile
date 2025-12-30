from fastapi import APIRouter
from controllers.user_controller import router as user_router
from controllers.role_controller import router as role_router
from controllers.post_controller import router as post_router


router = APIRouter()
router.include_router(user_router)
router.include_router(role_router)
router.include_router(post_router)
