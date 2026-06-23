# backend/app/services/sync_service.py
"""
同步任务服务
负责任务的启动、取消、状态查询
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Optional

from app.core.config import LOGS_DIR
from app.models.video import VideoCreate
from app.repositories import task_repo, video_repo
from app.scraper.auth_manager import AuthFileNotFoundError, AuthError
from app.scraper.sync_engine import fetch_favorites_list, SyncError

logger = logging.getLogger(__name__)

# 当前运行的任务引用
_current_task: Optional[asyncio.Task] = None


async def start_sync(task_id: str, limit: int = 10) -> Dict:
    """
    启动同步任务
    
    Args:
        task_id: 任务 ID
        limit: 最大拉取数量
    
    Returns:
        任务信息字典
    """
    global _current_task

    # 检查是否有正在运行的任务
    running = await task_repo.get_running_task()
    if running:
        raise RuntimeError("已有同步任务正在运行")

    # 创建任务记录
    task = await task_repo.create_task(task_id)

    # 启动异步任务
    _current_task = asyncio.create_task(_run_sync_task(task_id, limit))

    return task


async def cancel_sync(task_id: str) -> bool:
    """
    取消同步任务
    
    Args:
        task_id: 任务 ID
    
    Returns:
        是否成功取消
    """
    global _current_task

    task = await task_repo.get_task(task_id)
    if not task or task["status"] != "running":
        return False

    # 取消 asyncio 任务
    if _current_task and not _current_task.done():
        _current_task.cancel()
        try:
            await _current_task
        except asyncio.CancelledError:
            pass

    # 更新任务状态
    await task_repo.update_task(
        task_id,
        status="cancelled",
        finished_at=datetime.now().isoformat(),
    )

    _current_task = None
    return True


async def get_task_status(task_id: str) -> Optional[Dict]:
    """获取任务状态"""
    return await task_repo.get_task(task_id)


async def get_running_task() -> Optional[Dict]:
    """获取当前运行的任务"""
    return await task_repo.get_running_task()


async def _run_sync_task(task_id: str, limit: int):
    """
    执行同步任务的实际逻辑
    
    Args:
        task_id: 任务 ID
        limit: 最大拉取数量
    """
    try:
        logger.info(f"开始同步任务 {task_id}，限制数量: {limit}")

        # 调用爬虫获取视频
        new_videos = await fetch_favorites_list(limit=limit)

        if new_videos:
            # 获取已存在的 URL 集合（用于去重）
            existing_urls = await video_repo.get_existing_urls()

            videos_saved = 0
            for video_data in new_videos:
                if video_data["url"] not in existing_urls:
                    # 创建视频记录
                    video = VideoCreate(
                        url=video_data["url"],
                        title=video_data.get("title", ""),
                        author=video_data.get("author", ""),
                        desc=video_data.get("desc", ""),
                        summary=f"[AI总结] {video_data.get('title', '')} - {video_data.get('desc', '')[:50]}",
                        category="未分类",
                        tags=[],
                        scraped_at=video_data.get("scraped_at", datetime.now().isoformat()),
                    )
                    await video_repo.create_video(video)
                    existing_urls.add(video_data["url"])
                    videos_saved += 1

                    # 更新进度
                    await task_repo.update_task(
                        task_id,
                        progress=min(99, int(videos_saved / limit * 100)),
                        current_title=video_data.get("title", ""),
                    )

        # 标记任务完成
        await task_repo.complete_task(task_id)
        logger.info(f"同步任务 {task_id} 完成")

    except AuthFileNotFoundError as e:
        error_msg = f"登录态文件不存在: {e}"
        logger.error(error_msg)
        await task_repo.fail_task(task_id, error_msg)

    except AuthError as e:
        error_msg = f"登录态错误: {e}"
        logger.error(error_msg)
        await task_repo.fail_task(task_id, error_msg)

    except SyncError as e:
        error_msg = f"同步错误: {e}"
        logger.error(error_msg)
        await task_repo.fail_task(task_id, error_msg)

    except asyncio.CancelledError:
        logger.info(f"同步任务 {task_id} 被取消")
        raise

    except Exception as e:
        import traceback
        error_msg = f"未知错误: {type(e).__name__}: {e}"
        logger.error(error_msg, exc_info=True)
        await task_repo.fail_task(task_id, error_msg)

        # 写入错误日志文件
        log_file = LOGS_DIR / "sync_error.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"时间: {datetime.now().isoformat()}\n")
            f.write(f"任务ID: {task_id}\n")
            f.write(f"错误: {type(e).__name__}: {e}\n")
            f.write(traceback.format_exc())
            f.write(f"{'='*60}\n")
