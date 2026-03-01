import json
from typing import List

from app.db.repositories.cv_rag_repository import CvRagRepository
from app.services.openai_embeddings import get_embedding


DEFAULT_CHUNK_SIZE = 800
DEFAULT_OVERLAP = 150
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def _chunk_text(text: str, size: int, overlap: int) -> List[str]:
    """
    Jednoduché POC chunkování textu.
    Překryv zajišťuje zachování kontextu mezi chunky.
    """
    chunks: List[str] = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += size - overlap

    return chunks


class CvRagService:
    """
    Vytváří RAG reprezentaci CV a ukládá ji do DB.
    """

    def __init__(self, repo: CvRagRepository):
        self.repo = repo

    # ---------- PUBLIC API ----------

    def build_rag(self, cv_id: int, extracted_text: str):
        """
        Hlavní metoda:
        text → chunky → embeddings → JSON → DB
        """

        chunks = self._create_chunks(extracted_text)
        chunk_objects = self._create_embeddings(chunks)

        settings_json = self._build_settings_json()
        data_json = self._build_data_json(chunk_objects)

        return self.repo.upsert(
            cv_id=cv_id,
            settings_json=settings_json,
            data_json=data_json,
        )

    # ---------- INTERNAL STEPS ----------

    def _create_chunks(self, text: str) -> List[str]:
        if not text.strip():
            raise ValueError("Extracted text is empty")

        return _chunk_text(
            text=text,
            size=DEFAULT_CHUNK_SIZE,
            overlap=DEFAULT_OVERLAP,
        )

    def _create_embeddings(self, chunks: List[str]) -> List[dict]:
        """
        Pro každý chunk vytvoří embedding.
        """
        chunk_objects: List[dict] = []

        for index, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)

            chunk_objects.append(
                {
                    "index": index,
                    "text": chunk,
                    "embedding": embedding,
                }
            )

        return chunk_objects

    def _build_settings_json(self) -> str:
        settings = {
            "embedding_model": DEFAULT_EMBEDDING_MODEL,
            "chunk_size": DEFAULT_CHUNK_SIZE,
            "overlap": DEFAULT_OVERLAP,
        }
        return json.dumps(settings)

    def _build_data_json(self, chunk_objects: List[dict]) -> str:
        data = {"chunks": chunk_objects}
        return json.dumps(data)