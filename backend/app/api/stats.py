from fastapi import APIRouter

from app.config import settings
from app.database.sqlite_manager import db_manager
from app.database.chroma_manager import chroma_manager

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_stats():
    stats = db_manager.get_stats()
    stats["overview"]["total_embeddings"] = chroma_manager.count()
    return stats


@router.get("/config")
async def get_config_status():
    ai_provider = settings.AI_PROVIDER
    has_api_key = False

    if ai_provider == "deepseek":
        has_api_key = bool(settings.DEEPSEEK_API_KEY)
    elif ai_provider == "openai":
        has_api_key = bool(settings.OPENAI_API_KEY)
    elif ai_provider == "ollama":
        has_api_key = True  # Ollama 不需要 API Key

    return {
        "ai_provider": ai_provider,
        "has_api_key": has_api_key,
        "api_key_preview": _mask_api_key(
            settings.DEEPSEEK_API_KEY if ai_provider == "deepseek" else settings.OPENAI_API_KEY
        ) if has_api_key else None,
    }


def _mask_api_key(key: str) -> str:
    if not key or len(key) < 10:
        return "***"
    return key[:6] + "..." + key[-4:]
