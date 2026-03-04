from sqlalchemy import select, func, asc, desc
from sqlalchemy.dialects import mssql
from sqlalchemy.orm import Session, joinedload
from app.db.models.work_application import WorkApplication
from app.db.models.work import Work
from app.schemas.users.work_application_list_query import WorkApplicationListQuery
from app.schemas.users.work_application_list_item import WorkApplicationListItem
from sqlalchemy.sql import Select
from datetime import timedelta

class WorkApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- bezpečný whitelist pro sorting ---
    SORTABLE_COLUMNS = {
        "Id": WorkApplication.Id,
        "WorkName": Work.Name,
        "WorkCompany": Work.Company,
        "WorkProvider": Work.Provider,
        "CreatedAt": WorkApplication.CreatedAt,
        "UpdatedAt": WorkApplication.UpdatedAt,
        "Email": WorkApplication.Email,
        "Phone": WorkApplication.Phone,
        "Message": WorkApplication.Message,
        "Status": WorkApplication.Status
    }

    def list_by_user(self, user_id: int):
        return (
            self.db.query(WorkApplication)
            .filter(
                WorkApplication.UserId == user_id,
            )
            .order_by(WorkApplication.CreatedAt.desc())
            .all()
        )

    def list_by_user_and_work_ids(self,user_id: int, work_ids: list[int]) -> list[WorkApplication]:

        if not work_ids:
            return []

        stmt = (
            select(WorkApplication)
            .where(WorkApplication.UserId == user_id, WorkApplication.WorkId.in_(work_ids))
            .order_by(WorkApplication.CreatedAt.desc())
        )

        return list(self.db.scalars(stmt).all())
    
    def get(self, application_id: int):
        return (
            self.db.query(WorkApplication)
            .filter(
                WorkApplication.Id == application_id,
            )
            .first()
        )
    
    def get_by_user_and_work(self, user_id: int, work_id: int):
        return (
            self.db.query(WorkApplication)
            .filter(
                WorkApplication.UserId == user_id,
                WorkApplication.WorkId == work_id,
            )
            .first()
        )

    def create(self, **kwargs):
        application = WorkApplication(**kwargs)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def update(self, application: WorkApplication, **kwargs):
        for k, v in kwargs.items():
            setattr(application, k, v)

        self.db.commit()
        self.db.refresh(application)
        return application

    # ------------------------------------------------------------------
    # LIST BY FILTER
    # ------------------------------------------------------------------
    def list(self, user_id: int, query: WorkApplicationListQuery) -> tuple[list[WorkApplicationListItem], int]:
        """
        Returns paginated list of works with total count.
        """

        print('query', query)

        # --- base select ---
        stmt = (
            select(WorkApplication)
            .options(joinedload(WorkApplication.Work))
            .join(WorkApplication.Work)
        ).where(WorkApplication.UserId == user_id)

        print('query.filter', query.filter)

        
        # --- FILTERING ---

        if query.filter:

            if query.filter.WorkProvider:
                stmt = stmt.where(Work.Provider.ilike(f"%{query.filter.WorkProvider}%"))

            if query.filter.WorkName:
                stmt = stmt.where(Work.Name.ilike(f"%{query.filter.WorkName}%"))

            if query.filter.WorkCompany:
                stmt = stmt.where(Work.Company.ilike(f"%{query.filter.WorkCompany}%"))

            if query.filter.Phone:
                stmt = stmt.where(WorkApplication.Phone.ilike(f"%{query.filter.Phone}%"))

            if query.filter.Email:
                stmt = stmt.where(WorkApplication.Email.ilike(f"%{query.filter.Email}%"))

            if query.filter.Message:
                stmt = stmt.where(WorkApplication.Message.ilike(f"%{query.filter.Message}%"))

            if query.filter.Status:
                stmt = stmt.where(WorkApplication.Status.in_(query.filter.Status))

            if query.filter.CreatedFrom:
                stmt = stmt.where(WorkApplication.CreatedAt >= query.filter.CreatedFrom)

            if query.filter.CreatedTo:
                end = query.filter.CreatedTo + timedelta(days=1)
                stmt = stmt.where(WorkApplication.CreatedAt < end)

            if query.filter.UpdatedFrom:
                stmt = stmt.where(WorkApplication.UpdatedAt >= query.filter.UpdatedFrom)

            if query.filter.UpdatedTo:
                end = query.filter.UpdatedTo + timedelta(days=1)
                stmt = stmt.where(WorkApplication.UpdatedAt < end)
                

        # --- TOTAL COUNT (before paging) ---

        count_stmt = select(func.count()).select_from(stmt.subquery())
        # count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total: int = self.db.scalar(count_stmt) or 0
       
        # --- SORTING (safe whitelist) ---

        sort_column = self.SORTABLE_COLUMNS.get(query.SortColumn, WorkApplication.Id)

        stmt = stmt.order_by(
            asc(sort_column) if query.SortOrder == "asc" else desc(sort_column)
        )

      
        # --- PAGING ---

        offset = (query.Page - 1) * query.PageSize
        stmt = stmt.offset(offset).limit(query.PageSize)


        # --- EXECUTION ---

        items = list(self.db.scalars(stmt).all())

        WorkApplicationRepository.on_sql_command(stmt)

        return items, total
    
    @staticmethod
    def on_sql_command(stmt: Select):
        print("Executed SQL command:")
        sql = WorkApplicationRepository.get_sql(stmt)
        print(sql)
    
    @staticmethod
    def get_sql(stmt: Select) -> str:
        compiled = stmt.compile(
            dialect=mssql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
        return str(compiled)