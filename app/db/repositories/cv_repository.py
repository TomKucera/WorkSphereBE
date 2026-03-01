from sqlalchemy.orm import Session
from app.db.models.cv import Cv

from app.schemas.cvs.cv_list_query import CvListQuery
from app.schemas.cvs.cv_list_item import CvListItem
from sqlalchemy import select, func, asc, desc
from sqlalchemy.sql import Select
from datetime import datetime, timezone

class CvRepository:
    def __init__(self, db: Session):
        self.db = db

    SORTABLE_COLUMNS = {
        "Id": Cv.Id,
        "Name": Cv.Name,
        "Note": Cv.Note,
        "OriginalFileName": Cv.OriginalFileName,
        "ContentType": Cv.ContentType,
        "Active": Cv.Active,
        "CreatedAt": Cv.CreatedAt,
        "UpdatedAt": Cv.UpdatedAt,
    }

    # ------------------------------------------------------------------
    # LIST BY FILTER
    # ------------------------------------------------------------------
    def list(self, user_id: int, query: CvListQuery) -> tuple[list[CvListItem], int]:
        """
        Returns paginated list of CVs with total count.
        """

        print('query', query)

        # --- base select ---
        stmt = (
            select(Cv)
        ).where(Cv.UserId == user_id)

        print('query.filter', query.filter)

        
        # --- FILTERING ---

        if query.filter:

            if query.filter.Name:
                stmt = stmt.where(Cv.Name.ilike(f"%{query.filter.Name}%"))

            if query.filter.Note:
                stmt = stmt.where(Cv.Name.ilike(f"%{query.filter.Note}%"))

            if query.filter.OriginalFileName:
                stmt = stmt.where(Cv.OriginalFileName.ilike(f"%{query.filter.OriginalFileName}%"))
            
            if query.filter.Active is not None:
                stmt = stmt.where(Cv.Active == query.filter.Active)

            if query.filter.CreatedFrom:
                stmt = stmt.where(Cv.CreatedAt >= query.filter.CreatedFrom)

            if query.filter.CreatedTo:
                end = query.filter.CreatedTo + timedelta(days=1)
                stmt = stmt.where(Cv.CreatedAt < end)

            if query.filter.UpdatedFrom:
                stmt = stmt.where(Cv.UpdatedAt >= query.filter.UpdatedFrom)

            if query.filter.UpdatedTo:
                end = query.filter.UpdatedTo + timedelta(days=1)
                stmt = stmt.where(Cv.UpdatedAt < end)
                

        # --- TOTAL COUNT (before paging) ---

        count_stmt = select(func.count()).select_from(stmt.subquery())
        # count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total: int = self.db.scalar(count_stmt) or 0
       
        # --- SORTING (safe whitelist) ---

        sort_column = self.SORTABLE_COLUMNS.get(query.SortColumn, Cv.Id)

        stmt = stmt.order_by(
            asc(sort_column) if query.SortOrder == "asc" else desc(sort_column)
        )

      
        # --- PAGING ---

        offset = (query.Page - 1) * query.PageSize
        stmt = stmt.offset(offset).limit(query.PageSize)


        # --- EXECUTION ---

        items = list(self.db.scalars(stmt).all())

        # CvRepository.on_sql_command(stmt)

        return items, total

    def get_by_user(self, user_id: int, active: bool | None = True):
        query = (
            self.db.query(Cv).filter(Cv.UserId == user_id)
        )

        if active is not None:
            query = query.filter(Cv.Active == active)

        return (
            query.order_by(Cv.Id.asc()).all()
        )

    def get(self, cv_id: int, user_id: int, active: bool | None = True):

        query = (
            self.db.query(Cv).filter(Cv.Id == cv_id, Cv.UserId == user_id)
        )

        if active is not None:
            query = query.filter(Cv.Active == active)

        return (
            query.first()
        )
    
        # return (
        #     self.db.query(Cv)
        #     .filter(Cv.Id == cv_id, Cv.UserId == user_id)
        #     .first()
        # )
    
    def set_active(self, user_id: int, cv_id: int, active: bool) -> Cv | None:
        print('user_id', user_id)
        print('cv_id', cv_id)
        cv = (
            self.db.query(Cv)
            .filter(Cv.Id == cv_id, Cv.UserId == user_id)
            .first()
        )

        if not cv:
            return None

        cv.Active = active
        cv.UpdatedAt = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(cv)

        return cv

    def create(self, **kwargs):
        cv = Cv(**kwargs)
        self.db.add(cv)
        self.db.commit()
        self.db.refresh(cv)
        return cv

    def update(self, cv: Cv, **kwargs):
        for k, v in kwargs.items():
            setattr(cv, k, v)
        self.db.commit()
        self.db.refresh(cv)
        return cv
