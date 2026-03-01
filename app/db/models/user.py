from sqlalchemy import (
    Column,
    Integer,
    NVARCHAR,
    Boolean,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "Users"
    __table_args__ = (
        UniqueConstraint("Login", name="UQ_Users_Login"),
        CheckConstraint(
            "LEN([Login]) >= 5 AND LEN([Login]) <= 20",
            name="CK_Users_Login_Length",
        ),
        {"schema": "user"},
    )

    Id = Column(Integer, primary_key=True, index=True)

    Login = Column(NVARCHAR(20), nullable=False)
    PasswordHash = Column(NVARCHAR(200), nullable=False)

    FirstName = Column(NVARCHAR(100), nullable=True)
    LastName = Column(NVARCHAR(100), nullable=True)

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

    @property
    def display_name(self) -> str:
        parts = [
            (self.FirstName or "").strip(),
            (self.LastName or "").strip(),
        ]

        full_name = " ".join(p for p in parts if p)

        return full_name if full_name else self.Login

    # # Relationships
    # Contacts = relationship("UserContact", back_populates="User")
    # CVs = relationship("Cv", backref="User")