from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    NVARCHAR,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class WorkApplication(Base):
    __tablename__ = "WorkApplications"
    __table_args__ = (
        CheckConstraint(
            "[Status] IN ('SUBMITTED','VIEWED','REJECTED','ACCEPTED')",
            name="CK_WorkApplications_Status",
        ),
        CheckConstraint(
            "[ApplicationType] IN ('MANUAL','AUTO')",
            name="CK_WorkApplications_ApplicationType",
        ),
        {"schema": "user"},
    )

    Id = Column(Integer, primary_key=True, index=True)

    UserId = Column(
        Integer,
        ForeignKey("user.Users.Id"),
        nullable=False,
        index=True,
    )

    # WorkId = Column(Integer, nullable=False, index=True)
    WorkId = Column(
        Integer,
        ForeignKey("dbo.Works.Id"),
        nullable=False,
        index=True,
    )

    CvId = Column(
        Integer,
        ForeignKey("user.CVs.Id"),
        nullable=False,
        index=True,
    )

    FirstName = Column(NVARCHAR(100), nullable=False)
    LastName = Column(NVARCHAR(100), nullable=False)

    Email = Column(NVARCHAR(100), nullable=False)
    Phone = Column(NVARCHAR(100), nullable=False)

    Message = Column(NVARCHAR(1000), nullable=True)

    Status = Column(
        NVARCHAR(50),
        nullable=False,
        default="SUBMITTED",
        server_default="SUBMITTED",
    )

    ApplicationType = Column(
        NVARCHAR(20),
        nullable=False,
        default="MANUAL",
        server_default="MANUAL",
    )

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

    # Relationship
    Work = relationship("Work")
    