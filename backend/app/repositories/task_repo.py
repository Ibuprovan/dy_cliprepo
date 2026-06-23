# backend/app/repositories/task_repo.py
"""
任务状态仓库
封装所有同步任务相关的数据库操作
"""

from datetime import datetime
from typing import Dict, List, Optional

import aiosqlite

from app.db.database import get_db


async def init_task_table():
    """创建任务状态表"""
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS sync_tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'running',
            progress INTEGER DEFAULT 0,
            current_title TEXT DEFAULT '',
            error TEXT,
            started_at TEXT NOT NULL,
            finished_at TEXT
        )
    """)
    await db.commit()


async def create_task(task_id: str) -> Dict:
    """创建新任务"""
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        """
        INSERT INTO sync_tasks (task_id, status, progress, current_title, started_at)
        VALUES (?, 'running', 0, '', ?)
        """,
        (task_id, now),
    )
    await db.commit()
    return await get_task(task_id)


async def get_task(task_id: str) -> Optional[Dict]:
    """获取任务状态"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM sync_tasks WHERE task_id = ?", (task_id,)
    )
    row = await cursor.fetchone()
    if row:
        return _row_to_task(row)
    return None


async def get_running_task() -> Optional[Dict]:
    """获取当前正在运行的任务"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM sync_tasks WHERE status = 'running' ORDER BY started_at DESC LIMIT 1"
    )
    row = await cursor.fetchone()
    if row:
        return _row_to_task(row)
    return None


async def update_task(task_id: str, **kwargs) -> Optional[Dict]:
    """更新任务状态"""
    db = await get_db()

    # 构建更新语句
    updates = []
    params = []
    for key, value in kwargs.items():
        updates.append(f"{key} = ?")
        params.append(value)

    if not updates:
        return await get_task(task_id)

    params.append(task_id)
    query = f"UPDATE sync_tasks SET {', '.join(updates)} WHERE task_id = ?"
    await db.execute(query, params)
    await db.commit()

    return await get_task(task_id)


async def complete_task(task_id: str) -> Optional[Dict]:
    """标记任务完成"""
    return await update_task(
        task_id,
        status="completed",
        progress=100,
        current_title="",
        finished_at=datetime.now().isoformat(),
    )


async def fail_task(task_id: str, error: str) -> Optional[Dict]:
    """标记任务失败"""
    return await update_task(
        task_id,
        status="failed",
        error=error,
        finished_at=datetime.now().isoformat(),
    )


async def get_recent_tasks(limit: int = 10) -> List[Dict]:
    """获取最近的任务记录"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM sync_tasks ORDER BY started_at DESC LIMIT ?",
        (limit,),
    )
    rows = await cursor.fetchall()
    return [_row_to_task(row) for row in rows]


def _row_to_task(row: aiosqlite.Row) -> Dict:
    """将数据库行转换为任务字典"""
    return {
        "task_id": row["task_id"],
        "status": row["status"],
        "progress": row["progress"],
        "current_title": row["current_title"],
        "error": row["error"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
    }
