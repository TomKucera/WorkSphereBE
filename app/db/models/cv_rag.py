from sqlalchemy import Column, Integer, NVARCHAR, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.session import Base


class CvRag(Base):
    __tablename__ = "CvRags"
    __table_args__ = {"schema": "user"}

    CvId = Column(Integer, ForeignKey("user.CVs.Id", ondelete="CASCADE"), primary_key=True)

    RagSettingsJson = Column(NVARCHAR, nullable=False)
    RagDataJson = Column(NVARCHAR, nullable=False)

    CreatedAt = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    UpdatedAt = Column(
        DateTime(timezone=False),
        nullable=True,
        onupdate=func.sysutcdatetime(),
    )