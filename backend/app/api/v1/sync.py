# backend/app/api/v1/sync.py
"""
同步任务路由
"""

import asyncio
import json
import uuid

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.scraper.auth_manager import is_auth_exists
from app.services import sync_service

router = APIRouter()

SSE_TIMEOUT_SECONDS = 1800  # 30 分钟超时（修复 #10: 5 分钟对大量同步不够）


@router.post("/api/sync/start")
async def start_sync(limit: int = 10):
    """启动同步任务"""
    if not is_auth_exists():
        raise HTTPException(
            status_code=401,
            detail="请先运行 login_manual.py 完成抖音登录"
        )

    # 检查是否有正在运行的任务
    running = await sync_service.get_running_task()
    if running:
        raise HTTPException(
            status_code=409,
            detail="已有同步任务正在运行，请等待完成"
        )

    task_id = f"sync_{uuid.uuid4().hex[:8]}"

    try:
        task = await sync_service.start_sync(task_id, limit)
        return {
            "task_id": task_id,
            "status": "running",
            "message": "同步任务已启动",
        }
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/api/sync/stop")
async def stop_sync(task_id: Optional[str] = None):
    """停止同步任务"""
    if not task_id:
        # 查找当前运行的任务
        running = await sync_service.get_running_task()
        if not running:
            raise HTTPException(status_code=404, detail="没有正在运行的任务")
        task_id = running["task_id"]

    success = await sync_service.cancel_sync(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或已完成")

    return {"message": "任务已停止", "task_id": task_id}


@router.get("/api/sync/status/{task_id}")
async def sync_status(task_id: str):
    """获取同步任务状态（SSE）"""
    task = await sync_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_generator():
        elapsed = 0.0
        while elapsed < SSE_TIMEOUT_SECONDS:
            task = await sync_service.get_task_status(task_id)
            if not task:
                break

            data = {
                "task_id": task["task_id"],
                "status": task["status"],
                "progress": task["progress"],
                "current_title": task["current_title"],
                "error": task["error"],
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            if task["status"] in ("completed", "failed", "cancelled"):
                yield f"data: {json.dumps({'type': 'done', 'status': task['status']})}\n\n"
                break

            await asyncio.sleep(1)
            elapsed += 1

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
