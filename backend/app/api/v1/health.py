# backend/app/api/v1/health.py
"""
健康检查路由
"""

from fastapi import APIRouter

from app.scraper.auth_manager import is_auth_exists

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "auth_exists": is_auth_exists(),
    }
