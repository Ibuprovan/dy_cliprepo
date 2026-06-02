import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database.models import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.AUTH_DIR, exist_ok=True)
    os.makedirs(settings.CHROMADB_PATH, exist_ok=True)
    yield


app = FastAPI(
    title="抖音收藏 AI 知识库",
    description="抖音收藏视频的智能总结、分类与语义搜索",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.auth import router as auth_router
from app.api.sync import router as sync_router
from app.api.videos import router as videos_router
from app.api.search import router as search_router
from app.api.stats import router as stats_router

app.include_router(auth_router)
app.include_router(sync_router)
app.include_router(videos_router)
app.include_router(search_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {"message": "抖音收藏 AI 知识库 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# 静态文件挂载（生产模式）
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
