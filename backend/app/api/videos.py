from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database.sqlite_manager import db_manager

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("")
async def get_videos(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    min_quality: Optional[int] = None,
    sort_by: str = Query("synced_at", regex="^(synced_at|quality_score|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    result = db_manager.get_videos(
        page=page,
        size=size,
        category=category,
        tag=tag,
        min_quality=min_quality,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return result


@router.get("/{video_id}")
async def get_video(video_id: int):
    video = db_manager.get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return db_manager._video_to_dict(video)
