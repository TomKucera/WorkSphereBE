from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from app.db.session import Base


class WorkBookmark(Base):
    __tablename__ = "WorkBookmarks"
    __table_args__ = (
        UniqueConstraint("UserId", "WorkId", name="UQ_WorkBookmarks_User_Work"),
        {"schema": "user"},
    )

    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("user.Users.Id"), nullable=False, index=True)
    WorkId = Column(Integer, ForeignKey("dbo.Works.Id"), nullable=False, index=True)
    CreatedAt = Column(DateTime(timezone=False), nullable=False, server_default=func.sysutcdatetime())
