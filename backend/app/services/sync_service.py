import asyncio
import uuid
from datetime import datetime
from typing import Optional, Callable

from app.database.sqlite_manager import db_manager
from app.database.chroma_manager import chroma_manager
from app.ai.summarizer import AIProcessor
from app.scraper.douyin_scraper import scraper


class SyncTask:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = "running"
        self.progress = 0
        self.total = 0
        self.processed = 0
        self.current_title = ""
        self.error: Optional[str] = None


class SyncService:
    def __init__(self):
        self.tasks: dict[str, SyncTask] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}

    async def start_sync(self, max_videos: Optional[int] = None) -> str:
        task_id = f"sync_{uuid.uuid4().hex[:8]}"
        task = SyncTask(task_id)
        self.tasks[task_id] = task

        async_task = asyncio.create_task(self._run_sync(task, max_videos))
        self._running_tasks[task_id] = async_task

        return task_id

    async def _run_sync(self, task: SyncTask, max_videos: Optional[int]):
        try:
            ai_processor = AIProcessor()

            async def on_progress(data):
                if data["type"] == "found":
                    task.total = data["total"]
                    task.current_title = data["current"]["title"]

            new_videos = await scraper.scrape_favorites(
                max_count=max_videos,
                on_progress=on_progress,
            )

            task.total = len(new_videos)

            for i, video_data in enumerate(new_videos):
                if task.status == "stopped":
                    break

                existing = db_manager.get_video_by_url(video_data["url"])
                if existing:
                    task.processed = i + 1
                    continue

                task.current_title = video_data["title"]
                task.progress = int((i + 1) / len(new_videos) * 100)

                try:
                    ai_result = await ai_processor.process_video(
                        title=video_data["title"],
                        desc=video_data.get("desc", ""),
                        author=video_data.get("author", ""),
                    )
                except Exception as e:
                    ai_result = {
                        "summary": f"AI处理失败: {str(e)}",
                        "category": "其他",
                        "tags": [],
                        "key_points": [],
                        "quality_score": 1,
                    }

                video_record = {
                    "url": video_data["url"],
                    "title": video_data["title"],
                    "author": video_data.get("author", ""),
                    "author_id": video_data.get("author_id", ""),
                    "desc": video_data.get("desc", ""),
                    "cover_path": video_data.get("cover_url", ""),
                    "summary": ai_result["summary"],
                    "category": ai_result["category"],
                    "tags": ai_result["tags"],
                    "key_points": ai_result["key_points"],
                    "quality_score": ai_result["quality_score"],
                    "synced_at": datetime.utcnow(),
                }

                saved = db_manager.add_video(video_record)

                doc_text = f"{video_data['title']}. {ai_result['summary']}. 标签：{', '.join(ai_result['tags'])}"
                chroma_manager.add_embedding(
                    video_id=saved.id,
                    document=doc_text,
                    metadata={
                        "category": ai_result["category"],
                        "url": video_data["url"],
                    },
                )

                task.processed = i + 1
                await asyncio.sleep(0.1)

            task.status = "completed"
            task.progress = 100

            await scraper.save_cookies()
            await scraper.stop()

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally:
            if task.task_id in self._running_tasks:
                del self._running_tasks[task.task_id]

    def get_task(self, task_id: str) -> Optional[SyncTask]:
        return self.tasks.get(task_id)

    async def stop_sync(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == "running":
            task.status = "stopped"
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()
            return True
        return False

    async def manual_login(self) -> dict:
        result = await scraper.start(headless=False)
        await scraper.page.goto("https://www.douyin.com", wait_until="networkidle")
        return {
            "status": "waiting",
            "message": "浏览器已打开，请使用抖音APP扫码登录。登录完成后请调用 /api/auth/confirm 接口。",
        }

    async def confirm_login(self) -> dict:
        await scraper.save_cookies()
        await scraper.stop()
        return {"status": "success", "message": "登录态已保存"}


sync_service = SyncService()
