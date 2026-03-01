import json
from typing import List

from sqlalchemy.orm import Session

from app.db.models.cv_rag import CvRag
from app.db.models.work import Work

from app.db.repositories.work_repository import WorkRepository
from app.db.repositories.cv_repository import CvRepository
from app.db.repositories.cv_rag_repository import CvRagRepository

from app.services.embedding_service import EmbeddingService
from app.services.scraping_service import ScrapingService

from app.utils.similarity import cosine_similarity


class CvMatchingService:

    def __init__(self, db: Session):
        self.db = db

        self.work_repo = WorkRepository(db)
        self.cv_repo = CvRepository(db)
        self.cv_rag_repo = CvRagRepository(db)

        self.embedding_service = EmbeddingService()
        self.scraping_service = ScrapingService()

    def match(self, user_id: int, work_id: int):

        work = self.work_repo.get(work_id)
        if not work:
            raise ValueError("Work not found")

        # TODO: consider to take only relevant texts (e.g. requirements, responsibilities) instead of whole description to compute embedding and similarity
        job_text = self._resolve_work_text(work)

        # TODO: consider saving job embedding in the database to avoid recomputation on every match request
        job_embedding = self.embedding_service.get_embedding(job_text)

        cvs = self.cv_repo.get_by_user(user_id)
        cvs_by_id = {cv.Id: cv for cv in cvs}
        cv_ids = list(cvs_by_id.keys())

        cv_rags = self.cv_rag_repo.get_by_cv_ids(cv_ids)

        scoring_results: list[dict] = self._rank(cv_rags, job_embedding)

        for i in scoring_results:
            cv_id = i["cv_id"]
            cv = cvs_by_id.get(cv_id)
            i["cv_name"] = cv.OriginalFileName if cv else "Unknown CV"

        return scoring_results

    def _resolve_work_text(self, work: Work) -> str:

        scraped = self.scraping_service.get_work_text(work)

        if scraped and len(scraped) > 500:
            return scraped

        return work.Description

    def _rank(self, cv_rags: list[CvRag], job_embedding: list[float]):

        results = []

        for rag in cv_rags:

            rag_data = json.loads(rag.RagDataJson)

            best_similarity = 0.0

            for chunk in rag_data["chunks"]:
                sim = cosine_similarity(job_embedding, chunk["embedding"])
                best_similarity = max(best_similarity, sim)

            results.append({
                "cv_id": rag.CvId,
                "similarity_score": best_similarity
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)

        return results

        return {
            "evaluated_count": len(results),
            "results": results
        }
