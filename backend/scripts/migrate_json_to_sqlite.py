#!/usr/bin/env python3
"""
数据迁移脚本：将 videos.json 中的数据迁移到 SQLite
运行方式：cd backend && python scripts/migrate_json_to_sqlite.py
"""

import asyncio
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import DATA_DIR, VIDEOS_FILE
from app.db.database import init_db, get_db, close_db
from app.models.video import VideoCreate
from app.repositories import video_repo


async def migrate():
    """执行迁移"""
    print("=" * 60)
    print("  视频数据迁移：JSON → SQLite")
    print("=" * 60)
    print()

    # 检查 JSON 文件是否存在
    if not VIDEOS_FILE.exists():
        print(f"[跳过] JSON 文件不存在: {VIDEOS_FILE}")
        return

    # 读取 JSON 数据
    print(f"[1/4] 读取 JSON 文件: {VIDEOS_FILE}")
    try:
        with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
            videos_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[错误] 读取 JSON 文件失败: {e}")
        return

    print(f"       找到 {len(videos_data)} 条视频记录")

    if not videos_data:
        print("[跳过] 没有数据需要迁移")
        return

    # 备份 JSON 文件
    backup_file = VIDEOS_FILE.with_suffix(f".json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"[2/4] 备份 JSON 文件到: {backup_file}")
    shutil.copy2(VIDEOS_FILE, backup_file)
    print("       备份完成")

    # 初始化数据库
    print("[3/4] 初始化 SQLite 数据库")
    await init_db()
    print("       数据库初始化完成")

    # 迁移数据
    print("[4/4] 迁移数据到 SQLite")
    success_count = 0
    skip_count = 0
    error_count = 0

    for i, video_data in enumerate(videos_data, 1):
        try:
            # 构建 VideoCreate 对象
            video = VideoCreate(
                url=video_data.get("url", ""),
                title=video_data.get("title", ""),
                author=video_data.get("author", ""),
                desc=video_data.get("desc", ""),
                summary=video_data.get("summary", ""),
                category=video_data.get("category", "未分类"),
                tags=video_data.get("tags", []),
                scraped_at=video_data.get("scraped_at", datetime.now().isoformat()),
            )

            # 检查是否已存在
            existing = await video_repo.get_video_by_url(video.url)
            if existing:
                skip_count += 1
                continue

            # 插入数据库
            await video_repo.create_video(video)
            success_count += 1

            # 进度显示
            if i % 10 == 0 or i == len(videos_data):
                print(f"       进度: {i}/{len(videos_data)}", end="\r")

        except Exception as e:
            error_count += 1
            print(f"\n[警告] 迁移第 {i} 条记录失败: {e}")

    print()
    print()
    print("=" * 60)
    print("  迁移完成！")
    print("=" * 60)
    print(f"  成功: {success_count} 条")
    print(f"  跳过: {skip_count} 条（已存在）")
    print(f"  失败: {error_count} 条")
    print()
    print(f"  备份文件: {backup_file}")
    print(f"  数据库文件: {DATA_DIR / 'app.db'}")
    print()

    # 关闭数据库连接
    await close_db()


if __name__ == "__main__":
    asyncio.run(migrate())
