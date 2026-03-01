from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    DateTime,
    Boolean,
    NVARCHAR,
)
from sqlalchemy.sql import func

from app.db.session import Base

class Cv(Base):
    __tablename__ = "CVs"
    __table_args__ = {"schema": "user"}

    Id = Column(Integer, primary_key=True, index=True)

    Name = Column(NVARCHAR(50), nullable=False)
    Note = Column(NVARCHAR(300), nullable=True)

    UserId = Column(Integer, nullable=False, index=True)

    OriginalFileName = Column(NVARCHAR(255), nullable=False)
    ContentType = Column(NVARCHAR(100), nullable=True)

    FileContent = Column(LargeBinary, nullable=False)
    ExtractedText = Column(NVARCHAR, nullable=True)

    Active = Column(Boolean, nullable=False, default=True, server_default="1")

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