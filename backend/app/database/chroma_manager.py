from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class ChromaManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMADB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="video_embeddings",
            metadata={"hnsw:space": "cosine"},
        )

    def add_embedding(
        self,
        video_id: int,
        document: str,
        metadata: Optional[dict] = None,
    ) -> str:
        embedding_id = f"video_{video_id}"
        meta = metadata or {}
        meta["video_id"] = video_id

        self.collection.upsert(
            ids=[embedding_id],
            documents=[document],
            metadatas=[meta],
        )
        return embedding_id

    def search(
        self,
        query_text: str,
        n_results: int = 10,
        where: Optional[dict] = None,
    ) -> list:
        kwargs = {
            "query_texts": [query_text],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        items = []
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                item = {
                    "embedding_id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                }
                items.append(item)

        return items

    def delete_embedding(self, video_id: int) -> bool:
        try:
            self.collection.delete(ids=[f"video_{video_id}"])
            return True
        except Exception:
            return False

    def update_embedding(
        self,
        video_id: int,
        document: str,
        metadata: Optional[dict] = None,
    ) -> str:
        return self.add_embedding(video_id, document, metadata)

    def count(self) -> int:
        return self.collection.count()


chroma_manager = ChromaManager()
