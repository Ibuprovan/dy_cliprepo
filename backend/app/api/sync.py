from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import json

from app.services.sync_service import sync_service

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/start")
async def start_sync(max_videos: int = Query(None, description="最大同步数量")):
    for task in sync_service.tasks.values():
        if task.status == "running":
            raise HTTPException(status_code=409, detail="已有同步任务正在运行")

    task_id = await sync_service.start_sync(max_videos=max_videos)
    return {"task_id": task_id, "status": "running", "message": "同步任务已启动"}


@router.get("/status")
async def sync_status(task_id: str = Query(..., description="任务ID")):
    task = sync_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_generator():
        while True:
            task = sync_service.get_task(task_id)
            if not task:
                break

            data = {
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "total": task.total,
                "processed": task.processed,
                "current_title": task.current_title,
                "error": task.error,
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            if task.status in ("completed", "failed", "stopped"):
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/stop")
async def stop_sync(task_id: str = Query(..., description="任务ID")):
    success = await sync_service.stop_sync(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或已停止")
    return {"message": "同步任务已中止"}
