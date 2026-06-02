import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
