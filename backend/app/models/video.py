# backend/app/models/video.py
"""
视频数据模型
使用 Pydantic 定义数据验证和序列化
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VideoBase(BaseModel):
    """视频基础字段"""
    url: str
    title: str = ""
    author: str = ""
    author_id: str = ""
    desc: str = ""
    summary: str = ""
    category: str = "未分类"
    tags: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    quality_score: float = 0
    cover_url: str = ""
    cover_path: str = ""


class VideoCreate(VideoBase):
    """创建视频时使用的模型"""
    scraped_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class VideoUpdate(BaseModel):
    """更新视频时使用的模型（所有字段可选）"""
    title: Optional[str] = None
    author: Optional[str] = None
    desc: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    key_points: Optional[List[str]] = None
    quality_score: Optional[float] = None
    cover_url: Optional[str] = None


class VideoDB(VideoBase):
    """数据库中的视频记录"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    scraped_at: str
    created_at: str
    updated_at: str


class VideoResponse(VideoDB):
    """API 响应模型"""
    pass


class VideoListResponse(BaseModel):
    """视频列表响应"""
    items: List[VideoResponse]
    total: int
