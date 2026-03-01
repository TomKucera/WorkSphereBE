from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.scan import Scan


class ScanRepository:
    """
    Repository for Scan entity.

    Responsibilities:
    - CRUD operations
    - JSON-safe handling of Input/Output
    - Prepared for AI workflow updates
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # READ SINGLE
    # ------------------------------------------------------------------
    def get(self, scan_id: int) -> Optional[Scan]:
        """
        Get Scan by ID.
        """
        return self.db.get(Scan, scan_id)

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------
    def list(self, limit: int = 50) -> List[Scan]:
        """
        Return latest scans ordered by Id DESC.
        """
        stmt = (
            select(Scan)
            .order_by(Scan.Id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
