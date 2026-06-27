# backend/app/api/v1/videos.py
"""
视频相关路由
"""

from fastapi import APIRouter, HTTPException

from app.models.video import VideoListResponse, VideoResponse, VideoUpdate
from app.repositories import video_repo

router = APIRouter()


@router.get("/api/videos")
async def get_videos(limit: int = 100, offset: int = 0, category: str = None):
    """获取视频列表"""
    videos = await video_repo.get_videos(limit=limit, offset=offset, category=category)
    total = await video_repo.get_videos_count(category=category)
    return VideoListResponse(
        items=[VideoResponse.model_validate(v) for v in videos],
        total=total,
    )


@router.get("/api/videos/categories")
async def get_categories():
    """获取所有分类"""
    categories = await video_repo.get_categories()
    return {"categories": categories}


@router.get("/api/videos/{video_id}")
async def get_video(video_id: int):
    """获取单个视频"""
    video = await video_repo.get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return VideoResponse.model_validate(video)


@router.put("/api/videos/{video_id}")
async def update_video(video_id: int, updates: VideoUpdate):
    """更新视频信息（使用 VideoUpdate 模型做白名单校验，修复 #1）"""
    update_dict = updates.model_dump(exclude_unset=True)
    video = await video_repo.update_video(video_id, **update_dict)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return VideoResponse.model_validate(video)


@router.delete("/api/videos/{video_id}")
async def delete_video(video_id: int):
    """删除视频"""
    success = await video_repo.delete_video(video_id)
    if not success:
        raise HTTPException(status_code=404, detail="视频不存在")
    return {"message": "删除成功"}
