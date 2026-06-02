from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.database.sqlite_manager import db_manager
from app.database.chroma_manager import chroma_manager

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    category: Optional[str] = None
    mode: str = "semantic"


@router.post("")
async def search_videos(request: SearchRequest):
    if request.mode == "keyword":
        results = db_manager.search_videos(request.query)
        return {
            "results": results,
            "total": len(results),
            "query": request.query,
            "mode": "keyword",
        }

    where = None
    if request.category:
        where = {"category": request.category}

    chroma_results = chroma_manager.search(
        query_text=request.query,
        n_results=request.limit,
        where=where,
    )

    results = []
    for item in chroma_results:
        video_id = item["metadata"].get("video_id")
        if video_id:
            video = db_manager.get_video_by_id(video_id)
            if video:
                video_dict = db_manager._video_to_dict(video)
                video_dict["similarity"] = round(1 - item["distance"], 4)
                results.append(video_dict)

    return {
        "results": results,
        "total": len(results),
        "query": request.query,
        "mode": "semantic",
    }
