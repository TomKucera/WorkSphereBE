from typing import List

from app.services.openai_embeddings import get_embedding


class EmbeddingService:
    """
    Thin wrapper over OpenAI embeddings integration.
    Keeps call sites consistent and allows future enhancements
    (batching, retries, async, Azure OpenAI) without touching business logic.
    """

    def get_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []

        return get_embedding(text)
