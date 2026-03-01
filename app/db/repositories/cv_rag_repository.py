from typing import List
from sqlalchemy.orm import Session
from app.db.models.cv_rag import CvRag


class CvRagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, cv_id: int) -> CvRag | None:
        return self.db.query(CvRag).filter(CvRag.CvId == cv_id).first()

    def upsert(self, cv_id: int, settings_json: str, data_json: str) -> CvRag:
        rag = self.get(cv_id)

        if rag:
            rag.RagSettingsJson = settings_json
            rag.RagDataJson = data_json
        else:
            rag = CvRag(
                CvId=cv_id,
                RagSettingsJson=settings_json,
                RagDataJson=data_json,
            )
            self.db.add(rag)

        self.db.commit()
        self.db.refresh(rag)
        return rag
    
    def get_by_cv_ids(self, cv_ids: List[int]) -> List[CvRag]:
        if not cv_ids:
            return []

        return (
            self.db.query(CvRag)
            .filter(CvRag.CvId.in_(cv_ids))
            .all()
        )
