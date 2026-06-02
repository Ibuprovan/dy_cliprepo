from fastapi import APIRouter

from app.database.sqlite_manager import db_manager
from app.database.chroma_manager import chroma_manager

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats():
    stats = db_manager.get_stats()
    stats["overview"]["total_embeddings"] = chroma_manager.count()
    return stats
