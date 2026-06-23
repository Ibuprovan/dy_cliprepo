# backend/app/services/video_service.py
"""
视频业务逻辑服务
负责去重、摘要生成等业务逻辑
"""

from datetime import datetime
from typing import Dict, List, Set

from app.models.video import VideoCreate
from app.repositories import video_repo


def generate_summary(title: str, desc: str) -> str:
    """
    生成视频摘要
    当前为简单拼接，未来可接入 AI 服务
    
    Args:
        title: 视频标题
        desc: 视频描述
    
    Returns:
        摘要文本
    """
    # 截取描述的前50个字符
    desc_preview = desc[:50] if desc else ""
    return f"[AI总结] {title} - {desc_preview}"


async def save_videos_with_dedup(videos_data: List[Dict]) -> int:
    """
    保存视频列表（自动去重）
    
    Args:
        videos_data: 视频数据列表
    
    Returns:
        成功保存的视频数量
    """
    # 获取已存在的 URL 集合
    existing_urls = await video_repo.get_existing_urls()

    videos_saved = 0
    for video_data in videos_data:
        if video_data["url"] not in existing_urls:
            # 创建视频记录
            video = VideoCreate(
                url=video_data["url"],
                title=video_data.get("title", ""),
                author=video_data.get("author", ""),
                desc=video_data.get("desc", ""),
                summary=generate_summary(
                    video_data.get("title", ""),
                    video_data.get("desc", ""),
                ),
                category="未分类",
                tags=[],
                scraped_at=video_data.get("scraped_at", datetime.now().isoformat()),
            )
            await video_repo.create_video(video)
            existing_urls.add(video_data["url"])
            videos_saved += 1

    return videos_saved
