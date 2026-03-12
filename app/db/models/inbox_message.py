from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    NVARCHAR,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.db.session import Base


class InboxMessage(Base):
    __tablename__ = "InboxMessages"
    __table_args__ = (
        UniqueConstraint("UserId", "UserContactId", "GmailMessageId", name="UQ_InboxMessages_User_Contact_GmailMessage"),
        Index("IX_InboxMessages_User_Contact_ReceivedAt", "UserId", "UserContactId", "ReceivedAt"),
        {"schema": "user"},
    )

    Id = Column(Integer, primary_key=True, index=True)

    UserId = Column(Integer, ForeignKey("user.Users.Id"), nullable=False, index=True)
    UserContactId = Column(Integer, ForeignKey("user.UserContacts.Id"), nullable=False, index=True)
    WorkApplicationId = Column(Integer, ForeignKey("user.WorkApplications.Id"), nullable=True, index=True)

    GmailMessageId = Column(NVARCHAR(128), nullable=False)
    GmailThreadId = Column(NVARCHAR(128), nullable=True)

    FromEmail = Column(NVARCHAR(500), nullable=True)
    ToEmail = Column(NVARCHAR(500), nullable=True)
    Subject = Column(NVARCHAR(500), nullable=True)
    Snippet = Column(NVARCHAR(1000), nullable=True)

    ReceivedAt = Column(DateTime(timezone=False), nullable=False)
    ImportedAt = Column(DateTime(timezone=False), nullable=False, server_default=func.sysutcdatetime())
    ImportRunId = Column(NVARCHAR(36), nullable=False, index=True)

    Active = Column(Boolean, nullable=False, default=True, server_default="1")
    DeletedAt = Column(DateTime(timezone=False), nullable=True)
