from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.work_bookmark import WorkBookmark


class WorkBookmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_marked(self, user_id: int, work_id: int) -> bool:
        stmt = (
            select(WorkBookmark.Id)
            .where(
                WorkBookmark.UserId == user_id,
                WorkBookmark.WorkId == work_id,
            )
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def list_marked_work_ids(self, user_id: int, work_ids: list[int]) -> set[int]:
        if not work_ids:
            return set()

        stmt = (
            select(WorkBookmark.WorkId)
            .where(
                WorkBookmark.UserId == user_id,
                WorkBookmark.WorkId.in_(work_ids),
            )
        )
        return set(self.db.scalars(stmt).all())

    def create(self, user_id: int, work_id: int) -> WorkBookmark:
        bookmark = WorkBookmark(UserId=user_id, WorkId=work_id)
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark

    def delete(self, user_id: int, work_id: int) -> None:
        stmt = (
            select(WorkBookmark)
            .where(
                WorkBookmark.UserId == user_id,
                WorkBookmark.WorkId == work_id,
            )
            .limit(1)
        )
        bookmark = self.db.scalar(stmt)
        if bookmark is None:
            return

        self.db.delete(bookmark)
        self.db.commit()
