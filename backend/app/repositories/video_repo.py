# backend/app/repositories/video_repo.py
"""
视频数据仓库
封装所有视频相关的数据库操作
"""

import json
from typing import List, Optional, Set

import aiosqlite

from app.db.database import get_db
from app.models.video import VideoCreate, VideoDB

# 列名白名单，防止 SQL 注入（修复 #1）
ALLOWED_COLUMNS = {
    "title", "author", "desc", "summary", "category",
    "tags", "key_points", "quality_score", "cover_url", "cover_path",
}


def _safe_json_loads(s: str, default=None):
    """安全的 JSON 解析，防止脏数据导致崩溃（修复 #6）"""
    try:
        return json.loads(s) if s else (default if default is not None else [])
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


async def create_video(video: VideoCreate) -> VideoDB:
    """
    创建视频记录
    如果 URL 已存在，返回现有记录
    """
    db = await get_db()

    # 检查是否已存在
    existing = await get_video_by_url(video.url)
    if existing:
        return existing

    # 插入新记录
    cursor = await db.execute(
        """
        INSERT INTO videos (url, title, author, author_id, desc, summary, category, tags, key_points, quality_score, cover_url, cover_path, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video.url,
            video.title,
            video.author,
            video.author_id,
            video.desc,
            video.summary,
            video.category,
            json.dumps(video.tags, ensure_ascii=False),
            json.dumps(video.key_points, ensure_ascii=False),
            video.quality_score,
            video.cover_url,
            video.cover_path,
            video.scraped_at,
        ),
    )
    await db.commit()

    # 返回创建的记录
    return await get_video_by_id(cursor.lastrowid)


async def get_video_by_id(video_id: int) -> Optional[VideoDB]:
    """根据 ID 获取视频"""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    row = await cursor.fetchone()
    if row:
        return _row_to_video(row)
    return None


async def get_video_by_url(url: str) -> Optional[VideoDB]:
    """根据 URL 获取视频"""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM videos WHERE url = ?", (url,))
    row = await cursor.fetchone()
    if row:
        return _row_to_video(row)
    return None


async def get_videos(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
) -> List[VideoDB]:
    """
    获取视频列表
    支持分页和分类筛选
    """
    db = await get_db()

    query = "SELECT * FROM videos"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [_row_to_video(row) for row in rows]


async def get_videos_count(category: Optional[str] = None) -> int:
    """获取视频总数"""
    db = await get_db()

    query = "SELECT COUNT(*) FROM videos"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    cursor = await db.execute(query, params)
    row = await cursor.fetchone()
    return row[0]


async def get_existing_urls() -> Set[str]:
    """获取所有已存在的视频 URL（用于去重）"""
    db = await get_db()
    cursor = await db.execute("SELECT url FROM videos")
    rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def update_video(video_id: int, **kwargs) -> Optional[VideoDB]:
    """
    更新视频信息
    只更新传入的字段
    使用列名白名单防止 SQL 注入（修复 #1）
    """
    db = await get_db()

    # 构建更新语句
    updates = []
    params = []
    for key, value in kwargs.items():
        if key not in ALLOWED_COLUMNS:
            continue  # 忽略非法列名，防止 SQL 注入
        if key in ("tags", "key_points"):
            value = json.dumps(value, ensure_ascii=False)
        updates.append(f"{key} = ?")
        params.append(value)

    if not updates:
        return await get_video_by_id(video_id)

    # 添加 updated_at
    updates.append("updated_at = datetime('now')")
    params.append(video_id)

    query = f"UPDATE videos SET {', '.join(updates)} WHERE id = ?"
    await db.execute(query, params)
    await db.commit()

    return await get_video_by_id(video_id)


async def delete_video(video_id: int) -> bool:
    """删除单个视频"""
    db = await get_db()
    cursor = await db.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    await db.commit()
    return cursor.rowcount > 0


async def delete_videos(video_ids: List[int]) -> int:
    """批量删除视频，返回删除数量"""
    if not video_ids:
        return 0
    db = await get_db()
    placeholders = ",".join("?" for _ in video_ids)
    cursor = await db.execute(f"DELETE FROM videos WHERE id IN ({placeholders})", video_ids)
    await db.commit()
    return cursor.rowcount


async def get_categories() -> List[str]:
    """获取所有分类"""
    db = await get_db()
    cursor = await db.execute("SELECT DISTINCT category FROM videos ORDER BY category")
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


def _row_to_video(row: aiosqlite.Row) -> VideoDB:
    """将数据库行转换为 VideoDB 对象（使用安全 JSON 解析，修复 #6）"""
    return VideoDB(
        id=row["id"],
        url=row["url"],
        title=row["title"],
        author=row["author"],
        author_id=row["author_id"],
        desc=row["desc"],
        summary=row["summary"],
        category=row["category"],
        tags=_safe_json_loads(row["tags"], []),
        key_points=_safe_json_loads(row["key_points"], []),
        quality_score=row["quality_score"],
        cover_url=row["cover_url"],
        cover_path=row["cover_path"],
        scraped_at=row["scraped_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
