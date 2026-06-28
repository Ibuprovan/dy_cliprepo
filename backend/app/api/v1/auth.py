from fastapi import APIRouter

from app.scraper.auth_manager import is_auth_exists, delete_auth

router = APIRouter()


@router.get("/api/auth/status")
async def auth_status():
    """获取登录状态"""
    return {
        "logged_in": is_auth_exists(),
        "message": "已登录" if is_auth_exists() else "未登录",
    }


@router.post("/api/auth/logout")
async def logout():
    """退出登录：删除登录态文件"""
    success = delete_auth()
    return {
        "success": success,
        "logged_in": is_auth_exists(),
        "message": "已退出登录" if success else "退出失败或未登录",
    }
