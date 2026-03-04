from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    NVARCHAR,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class WorkDescription(Base):
    __tablename__ = "WorkDescriptions"
    __table_args__ = {"schema": "user"}

    UserId = Column(
        Integer,
        ForeignKey("user.Users.Id"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    WorkId = Column(
        Integer,
        ForeignKey("dbo.Works.Id"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    Description = Column(
        NVARCHAR(None),  # NVARCHAR(MAX)
        nullable=False,
    )

    UpdatedAt = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.sysutcdatetime(),
        onupdate=func.sysutcdatetime(),
    )

    # # Relationships
    # User = relationship("User")
    # Work = relationship("Work")