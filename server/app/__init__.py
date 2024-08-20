from fastapi import APIRouter

router = APIRouter()

from . import admin, user, websocket

router.include_router(admin.router)
router.include_router(user.router)
