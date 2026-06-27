# backend/app/main.py
"""
抖音收藏AI知识库 - FastAPI主入口
MVP版本：最小可用Demo
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import ensure_dirs, FRONTEND_DIST_DIR
from app.api.v1 import router as api_router
from app.scraper.sync_engine import setup_sync_logger
from app.db.database import init_db, close_db

# 修复 #12: 在 main.py 中也设置事件循环策略，作为热重载保险
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    ensure_dirs()
    setup_sync_logger()
    await init_db()
    yield
    # 关闭时执行
    await close_db()


# 创建FastAPI应用
app = FastAPI(
    title="抖音收藏AI知识库",
    description="抖音收藏视频的智能总结与展示",
    version="1.0.0-mvp",
    lifespan=lifespan,
)

# CORS配置
# 为什么需要：前端开发服务器(5173)和后端(8000)端口不同
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "抖音收藏AI知识库",
        "version": "1.0.0-mvp",
        "docs": "/docs",
    }


# 静态文件挂载（生产模式）
# 为什么检查目录是否存在：开发模式下前端目录可能不存在
if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA路由（修复 #2 路径穿越 + #4 API 404 被吞掉）"""
        # API 路径不走 SPA fallback
        if full_path.startswith("api/") or full_path == "health":
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # 路径穿越防护：解析后必须在 FRONTEND_DIST_DIR 内
        base = Path(FRONTEND_DIST_DIR).resolve()
        file_path = (base / full_path).resolve()
        if not str(file_path).startswith(str(base)):
            raise HTTPException(status_code=403, detail="Forbidden")

        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(base / "index.html"))
