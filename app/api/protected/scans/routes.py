from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user

from app.db.deps import get_db
from app.db.repositories.scan_repository import ScanRepository
from app.schemas.scans.scan_list_item import ScanListItem

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.get("", response_model=list[ScanListItem])
def list_scans(
    limit: int = 50,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print("USER ID =", user_id)
    repo = ScanRepository(db)
    return repo.list(limit)
