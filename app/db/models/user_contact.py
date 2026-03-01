from sqlalchemy import (
    Column,
    Integer,
    NVARCHAR,
    Boolean,
    DateTime,
    CheckConstraint,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base

class UserContact(Base):
    __tablename__ = "UserContacts"
    __table_args__ = (
        CheckConstraint(
            "[Type] IN ('Email','Phone')",
            name="CK_UserContacts_Type",
        ),
        Index(
            "UX_UserContacts_Primary",
            "UserId",
            "Type",
            unique=True,
            mssql_where=text("[IsPrimary] = 1 AND [Active] = 1"),
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

    Type = Column(NVARCHAR(20), nullable=False)
    Value = Column(NVARCHAR(100), nullable=False)

    IsPrimary = Column(Boolean, nullable=False, default=False, server_default="0")
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

    # # Relationship
    # User = relationship("User", back_populates="Contacts")