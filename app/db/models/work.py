from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey

from sqlalchemy.orm import relationship

from app.db.session import Base


class Work(Base):
    __tablename__ = "Works"
    __table_args__ = {"schema": "dbo"}

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    Provider: Mapped[str] = mapped_column(String(20), nullable=False)
    OriginalId: Mapped[str] = mapped_column(String(50), nullable=False)

    Name: Mapped[str] = mapped_column(String(500), nullable=False)
    Description: Mapped[str] = mapped_column(Text, nullable=False)
    Url: Mapped[str] = mapped_column(String(500), nullable=False)
    Company: Mapped[str] = mapped_column(String(500), nullable=False)

    MainArea: Mapped[str] = mapped_column(String(500), nullable=False)
    Collaborations: Mapped[str] = mapped_column(String(500), nullable=False)
    Areas: Mapped[str] = mapped_column(String(500), nullable=False)
    Seniorities: Mapped[str] = mapped_column(String(500), nullable=False)

    AddedByScanId: Mapped[int] = mapped_column(ForeignKey("dbo.Scans.Id"), nullable=False)
    RemovedByScanId: Mapped[int | None] = mapped_column(ForeignKey("dbo.Scans.Id"))

    ValidFrom: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ValidTo: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    SnapshotFileName: Mapped[str | None] = mapped_column(String(50))
    RemoteRatio: Mapped[int | None] = mapped_column(Integer)
    SalaryCurrency: Mapped[str | None] = mapped_column(String(3))
    SalaryMax: Mapped[int | None] = mapped_column(Integer)
    SalaryMin: Mapped[int | None] = mapped_column(Integer)

    # Relationship
    AddedByScan = relationship("Scan", foreign_keys=[AddedByScanId])
    RemovedByScan = relationship("Scan", foreign_keys=[RemovedByScanId])
