from typing import Optional
from openai import OpenAI

from app.config import settings


class EmbeddingProcessor:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.AI_PROVIDER
        self._init_client()

    def _init_client(self):
        if self.provider == "ollama":
            self.client = OpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama",
            )
            self.model = "nomic-embed-text"
        elif self.provider == "deepseek":
            self.client = OpenAI(
                base_url=settings.DEEPSEEK_BASE_URL,
                api_key=settings.DEEPSEEK_API_KEY,
            )
            self.model = "text-embedding-v1"
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "text-embedding-3-small"

    async def get_embedding(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception:
            return []
