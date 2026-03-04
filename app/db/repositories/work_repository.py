from typing import List, Optional
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects import mssql
from sqlalchemy import select, and_, or_, func, asc, desc, exists
from sqlalchemy.sql import Select
from datetime import timedelta

from app.db.models.scan import Scan
from app.db.models.work import Work
from app.db.models.work_description import WorkDescription
from app.db.models.work_application import WorkApplication
from app.schemas.works.work_list_query import WorkListQuery
from app.schemas.works.work_list_item import WorkListItem

class WorkRepository:

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # GET BY ID
    # ------------------------------------------------------------------
    def get(self, work_id: int) -> Optional[Work]:
        return self.db.get(Work, work_id)
    
    # ------------------------------------------------------------------
    # UPSERT DESCRIPTION
    # ------------------------------------------------------------------
    def get_work_description(self, user_id: int, work_id: int) -> Optional[WorkDescription]:
        return self.db.get(WorkDescription,{"UserId": user_id, "WorkId": work_id})
    
    def get_work_descriptions_by_work_ids(self, user_id: int, work_ids: list[int]) -> list[WorkDescription]:
        if not work_ids:
            return []

        stmt = (
            select(WorkDescription)
            .where(WorkDescription.UserId == user_id, WorkDescription.WorkId.in_(work_ids))
        )

        return list(self.db.scalars(stmt).all())
    
    def upsert_work_description(self, user_id: int, work_id: int, description: str) -> WorkDescription:
        """
        Insert or update user-specific work description.
        Composite PK: (UserId, WorkId)
        """

        entity = self.db.get(WorkDescription, {"UserId": user_id, "WorkId": work_id})

        if entity:
            entity.Description = description
            # UpdatedAt se nastaví přes onupdate=func.sysutcdatetime()
        else:
            entity = WorkDescription(
                UserId=user_id,
                WorkId=work_id,
                Description=description,
            )
            self.db.add(entity)

        self.db.commit()
        self.db.refresh(entity)
        return entity

    # # ------------------------------------------------------------------
    # # LIST (latest active)
    # # ------------------------------------------------------------------
    # def list(self, limit: int = 50) -> List[Work]:
    #     stmt = (
    #         select(Work)
    #         .where(Work.RemovedByScanId.is_(None))
    #         .order_by(Work.Id.desc())
    #         .limit(limit)
    #     )
    #     return list(self.db.scalars(stmt).all())

    # ------------------------------------------------------------------
    # LIST BY PROVIDER
    # ------------------------------------------------------------------
    def list_by_provider(self, provider: str, limit: int = 50) -> List[Work]:
        stmt = (
            select(Work)
            .where(
                Work.Provider == provider,
                Work.RemovedByScanId.is_(None),
            )
            .order_by(Work.Id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    # ------------------------------------------------------------------
    # LIST BY SCAN
    # ------------------------------------------------------------------
    def list_by_scan(self, scan_id: int) -> List[Work]:
        stmt = (
            select(Work)
            .where(
                or_(
                    Work.AddedByScanId == scan_id,
                    Work.RemovedByScanId == scan_id,
                )
            )
            .order_by(Work.Id.asc())
        )
        return list(self.db.scalars(stmt).all())

    # ------------------------------------------------------------------
    # LIST BY FILTER
    # ------------------------------------------------------------------
    def list(self, user_id: int, query: WorkListQuery) -> tuple[list[WorkListItem], int]:
        """
        Returns paginated list of works with total count.
        """

        # --- base select ---
        AddedScan = aliased(Scan)
        RemovedScan = aliased(Scan)
        
        stmt = select(Work)
        stmt = stmt.outerjoin(AddedScan, Work.AddedByScanId == AddedScan.Id)
        stmt = stmt.outerjoin(RemovedScan, Work.RemovedByScanId == RemovedScan.Id)

        SORTABLE_COLUMNS = {
            "Id": Work.Id,
            "Provider": Work.Provider,
            "OriginalId": Work.Provider,
            "Company": Work.Company,
            "Name": Work.Name,
            "Description": Work.Description,
            "Salary": Work.SalaryMin,
            "Remote": Work.RemoteRatio,
            "CreatedAt": AddedScan.EndedAt,
            "DeletedAt": RemovedScan.EndedAt,
        }

        # --- FILTERING ---
        if query.filter:

            f = query.filter

            if f.Provider:
                stmt = stmt.where(Work.Provider.ilike(f"%{f.Provider}%"))

            if f.OriginalId:
                stmt = stmt.where(Work.OriginalId.ilike(f"%{f.OriginalId}%"))

            if f.Company:
                stmt = stmt.where(Work.Company.ilike(f"%{f.Company}%"))

            if f.Name:
                stmt = stmt.where(Work.Name.ilike(f"%{f.Name}%"))

            if f.Description:
                stmt = stmt.where(Work.Description.ilike(f"%{f.Description}%"))

            if f.Salary is not None:
                stmt = stmt.where(Work.SalaryMin >= f.Salary)

            if f.Remote is not None:
                stmt = stmt.where(Work.RemoteRatio >= f.Remote)

            # --- ACTIVE FLAG ---
            if f.Active is True:
                stmt = stmt.where(Work.RemovedByScanId.is_(None))

            elif f.Active is False:
                stmt = stmt.where(Work.RemovedByScanId.isnot(None))

            # --- CREATED FILTER (AddedScan) ---
            if f.CreatedFrom:
                stmt = stmt.where(AddedScan.EndedAt >= f.CreatedFrom)

            if f.CreatedTo:
                end = f.CreatedTo + timedelta(days=1)
                stmt = stmt.where(AddedScan.EndedAt < end)

            # --- DELETED FILTER (RemovedScan) ---
            if f.DeletedFrom:
                stmt = stmt.where(RemovedScan.EndedAt >= f.DeletedFrom)

            if f.DeletedTo:
                end = f.DeletedTo + timedelta(days=1)
                stmt = stmt.where(RemovedScan.EndedAt < end)
            
            if f.Application is True:
                stmt = stmt.where(
                    exists().where(
                        and_(WorkApplication.WorkId == Work.Id,WorkApplication.UserId == user_id)
                    )
                )

            elif f.Application is False:
                stmt = stmt.where(
                    ~exists().where(
                        and_(WorkApplication.WorkId == Work.Id, WorkApplication.UserId == user_id)
                    )
                )


        # --- TOTAL COUNT (before paging) ---
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self.db.scalar(count_stmt) or 0

        # --- SORTING (safe whitelist) ---
        sort_column = SORTABLE_COLUMNS.get(query.SortColumn, Work.Id)        
        stmt = stmt.order_by(
            asc(sort_column) if query.SortOrder == "asc" else desc(sort_column)
        )

        # --- PAGING ---
        offset = (query.Page - 1) * query.PageSize
        stmt = stmt.offset(offset).limit(query.PageSize)

        # --- EAGER LOADING ---
        stmt = stmt.options(
            joinedload(Work.AddedByScan),
            joinedload(Work.RemovedByScan),
        )

        # --- EXECUTION ---
        items = list(self.db.scalars(stmt).all())
        WorkRepository.on_sql_command(stmt)

        return items, total
    
    @staticmethod
    def on_sql_command(stmt: Select):
        print("Executed SQL command:")
        sql = WorkRepository.get_sql(stmt)
        print(sql)
    
    @staticmethod
    def get_sql(stmt: Select) -> str:
        compiled = stmt.compile(
            dialect=mssql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
        return str(compiled)