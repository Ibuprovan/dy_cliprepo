from fastapi import APIRouter, Query

from app.core.logger import get_recent_logs

router = APIRouter()


@router.get("/api/debug/logs")
async def get_logs(
    n: int = Query(100, ge=1, le=500, description="返回条数"),
    level: str = Query("DEBUG", description="最低日志级别"),
):
    """获取最近日志（用于调试）"""
    logs = get_recent_logs(n=n, min_level=level)
    return {"logs": logs, "count": len(logs)}
