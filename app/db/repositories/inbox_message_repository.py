from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.inbox_message import InboxMessage


class InboxMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_last_received_at(self, user_id: int, contact_id: int) -> datetime | None:
        stmt = (
            select(func.max(InboxMessage.ReceivedAt))
            .where(
                InboxMessage.UserId == user_id,
                InboxMessage.UserContactId == contact_id,
            )
        )
        return self.db.scalar(stmt)

    def get_last_import_run_id(self, user_id: int, contact_id: int) -> str | None:
        stmt = (
            select(InboxMessage.ImportRunId)
            .where(
                InboxMessage.UserId == user_id,
                InboxMessage.UserContactId == contact_id,
                InboxMessage.Active == True,
            )
            .order_by(InboxMessage.ImportedAt.desc(), InboxMessage.Id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def count_active_by_contact(self, user_id: int, contact_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(InboxMessage)
            .where(
                InboxMessage.UserId == user_id,
                InboxMessage.UserContactId == contact_id,
                InboxMessage.Active == True,
            )
        )
        return self.db.scalar(stmt) or 0

    def exists_by_gmail_message_id(self, user_id: int, contact_id: int, gmail_message_id: str) -> bool:
        stmt = (
            select(InboxMessage.Id)
            .where(
                InboxMessage.UserId == user_id,
                InboxMessage.UserContactId == contact_id,
                InboxMessage.GmailMessageId == gmail_message_id,
            )
            .limit(1)
        )
        return self.db.scalar(stmt) is not None

    def create_many(self, items: list[dict]) -> list[InboxMessage]:
        entities = [InboxMessage(**item) for item in items]
        self.db.add_all(entities)
        self.db.commit()
        for entity in entities:
            self.db.refresh(entity)
        return entities

    def list_by_contact(
        self,
        user_id: int,
        contact_id: int,
        import_run_id: str | None = None,
        only_unassigned: bool = False,
        active_only: bool = True,
    ) -> list[InboxMessage]:
        stmt = (
            select(InboxMessage)
            .where(
                InboxMessage.UserId == user_id,
                InboxMessage.UserContactId == contact_id,
            )
            .order_by(InboxMessage.ReceivedAt.desc(), InboxMessage.Id.desc())
        )

        if import_run_id:
            stmt = stmt.where(InboxMessage.ImportRunId == import_run_id)

        if only_unassigned:
            stmt = stmt.where(InboxMessage.WorkApplicationId.is_(None))

        if active_only:
            stmt = stmt.where(InboxMessage.Active == True)

        return list(self.db.scalars(stmt).all())

    def get(self, message_id: int, user_id: int) -> InboxMessage | None:
        stmt = (
            select(InboxMessage)
            .where(
                InboxMessage.Id == message_id,
                InboxMessage.UserId == user_id,
            )
            .limit(1)
        )
        return self.db.scalar(stmt)

    def assign(self, message: InboxMessage, work_application_id: int) -> InboxMessage:
        message.WorkApplicationId = work_application_id
        self.db.commit()
        self.db.refresh(message)
        return message

    def soft_delete(self, message: InboxMessage) -> None:
        message.Active = False
        message.DeletedAt = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
