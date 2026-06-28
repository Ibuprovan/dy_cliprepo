from fastapi import APIRouter

from .health import router as health_router
from .videos import router as videos_router
from .sync import router as sync_router
from .auth import router as auth_router
from .debug import router as debug_router

router = APIRouter()
router.include_router(health_router)
router.include_router(videos_router)
router.include_router(sync_router)
router.include_router(auth_router)
router.include_router(debug_router)
