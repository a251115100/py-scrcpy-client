from fastapi import APIRouter

router = APIRouter()

from . import api_admin, api_user, websocket

router.include_router(api_admin.router)
router.include_router(api_user.router)
