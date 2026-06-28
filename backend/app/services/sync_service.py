# backend/app/services/sync_service.py
"""
同步任务服务
负责任务的启动、取消、状态查询

关键设计：同步任务在独立线程中运行，避免 uvicorn 事件循环与 Playwright 子进程冲突。
ProactorEventLoopPolicy 只在主线程设置一次不够，uvicorn reload 后的 worker 进程会丢失。
独立线程 + 独立事件循环 = 可靠运行。
"""

import asyncio
import logging
import sys
import threading
from datetime import datetime
from typing import Dict, Optional

from app.core.config import LOGS_DIR
from app.models.video import VideoCreate
from app.repositories import task_repo, video_repo
from app.scraper.auth_manager import AuthFileNotFoundError, AuthError
from app.scraper.sync_engine import fetch_favorites_list, SyncError
from app.services.ai_service import generate_summary_and_category

logger = logging.getLogger(__name__)

# 当前运行的线程引用
_current_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


async def start_sync(task_id: str, limit: int = 10) -> Dict:
    """
    启动同步任务（在独立线程中运行）
    """
    global _current_thread, _stop_event

    # 检查是否有正在运行的任务
    running = await task_repo.get_running_task()
    if running:
        raise RuntimeError("已有同步任务正在运行")

    # 创建任务记录
    task = await task_repo.create_task(task_id)

    # 重置停止信号
    _stop_event.clear()

    # 在独立线程中启动同步任务
    _current_thread = threading.Thread(
        target=_run_sync_in_thread,
        args=(task_id, limit),
        daemon=True,
    )
    _current_thread.start()

    return task


def _run_sync_in_thread(task_id: str, limit: int):
    """
    在独立线程中运行同步任务
    创建独立的事件循环，避免与 uvicorn 事件循环冲突
    """
    # 在线程中设置事件循环策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_run_sync_task(task_id, limit))
    except Exception as e:
        logger.error(f"线程中同步任务异常: {e}", exc_info=True)
    finally:
        loop.close()


async def cancel_sync(task_id: str) -> bool:
    """
    取消同步任务
    """
    global _current_thread, _stop_event

    task = await task_repo.get_task(task_id)
    if not task or task["status"] != "running":
        return False

    # 设置停止信号
    _stop_event.set()

    # 更新任务状态
    await task_repo.update_task(
        task_id,
        status="cancelled",
        finished_at=datetime.now().isoformat(),
    )

    _current_thread = None
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
                # 检查是否需要停止
                if _stop_event.is_set():
                    logger.info(f"同步任务 {task_id} 收到停止信号")
                    break

                if video_data["url"] not in existing_urls:
                    title = video_data.get("title", "")
                    desc = video_data.get("desc", "")
                    summary, category = await generate_summary_and_category(title, desc)

                    video = VideoCreate(
                        url=video_data["url"],
                        title=title,
                        author=video_data.get("author", ""),
                        desc=desc,
                        summary=summary,
                        category=category,
                        cover_url=video_data.get("cover_url", ""),
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
        log_content = (
            f"\n{'='*60}\n"
            f"时间: {datetime.now().isoformat()}\n"
            f"任务ID: {task_id}\n"
            f"错误: {type(e).__name__}: {e}\n"
            f"{traceback.format_exc()}"
            f"{'='*60}\n"
        )
        await asyncio.to_thread(_write_log, log_file, log_content)


def _write_log(log_file, content):
    """同步写入日志文件的辅助函数"""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(content)
