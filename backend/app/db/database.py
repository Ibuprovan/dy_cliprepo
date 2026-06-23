# backend/app/db/database.py
"""
SQLite 数据库连接管理
使用 aiosqlite 实现异步数据库操作
"""

import aiosqlite
from pathlib import Path
from app.core.config import DATA_DIR

# 数据库文件路径
DB_FILE = DATA_DIR / "app.db"

# 全局连接引用
_db_connection: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    """
    获取数据库连接（单例模式）
    为什么用单例：避免频繁创建/关闭连接，提高性能
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(str(DB_FILE))
        _db_connection.row_factory = aiosqlite.Row
        # 启用 WAL 模式，提高并发读写性能
        await _db_connection.execute("PRAGMA journal_mode=WAL")
        # 启用外键约束
        await _db_connection.execute("PRAGMA foreign_keys=ON")
    return _db_connection


async def close_db():
    """关闭数据库连接"""
    global _db_connection
    if _db_connection is not None:
        await _db_connection.close()
        _db_connection = None


async def init_db():
    """
    初始化数据库表结构
    应在应用启动时调用
    """
    db = await get_db()
    await _create_tables(db)
    await db.commit()


async def _create_tables(db: aiosqlite.Connection):
    """创建所有数据表"""
    # 视频表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            author TEXT NOT NULL DEFAULT '',
            author_id TEXT NOT NULL DEFAULT '',
            desc TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT '未分类',
            tags TEXT NOT NULL DEFAULT '[]',
            key_points TEXT NOT NULL DEFAULT '[]',
            quality_score REAL DEFAULT 0,
            cover_url TEXT NOT NULL DEFAULT '',
            cover_path TEXT NOT NULL DEFAULT '',
            scraped_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # 创建索引
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_videos_url ON videos(url)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_videos_category ON videos(category)
    """)

    # 同步任务表
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
