import json
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text
from app.db.session import Base

EMPTY_PROVIDER = {
    "AddedOriginalIds": [],
    "RemovedOriginalIds": [],
    "InvalidOriginalIds": [],
}

class Scan(Base):
    __tablename__ = "Scans"
    __table_args__ = {"schema": "dbo"}

    Id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _Input: Mapped[str] = mapped_column("Input", String(1000), nullable=False)
    _Output: Mapped[str | None] = mapped_column("Output", Text, nullable=True)
    StartedAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    EndedAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # --- JSON helpers ---

    @property
    def Input(self) -> dict:
        return json.loads(self._Input)

    @Input.setter
    def Input(self, value: dict):
        self._Input = json.dumps(value)

    # @property
    # def Output(self) -> dict | None:
    #     return json.loads(self._Output) if self._Output else None

    @property
    def Output(self) -> dict | None:
        if not self._Output:
            return None

        data = json.loads(self._Output)

        # ensure all providers exist
        for provider in ["StartupJobs", "CoolJobs", "JobStackIT", "Titans", "JobsCZ"]:
            data.setdefault(provider, EMPTY_PROVIDER.copy())

        return data

    @Output.setter
    def Output(self, value: dict | None):
        self._Output = json.dumps(value) if value else None
