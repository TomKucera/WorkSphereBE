from sqlalchemy.orm import Session
from app.db.models.user_contact import UserContact


class UserContactRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, user_id: int):
        return (
            self.db.query(UserContact)
            .filter(UserContact.UserId == user_id, UserContact.Active == True)
            .order_by(UserContact.CreatedAt.desc())
            .all()
        )

    def get(self, contact_id: int, user_id: int):
        return (
            self.db.query(UserContact)
            .filter(
                UserContact.Id == contact_id,
                UserContact.UserId == user_id,
                UserContact.Active == True,
            )
            .first()
        )

    def create(self, **kwargs):
        contact = UserContact(**kwargs)
        self.db.add(contact)
        self.db.flush()  # důležité pro získání Id bez commit

        if contact.IsPrimary:
            self._clear_existing_primary(contact)

        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update(self, contact: UserContact, **kwargs):
        for k, v in kwargs.items():
            setattr(contact, k, v)

        if contact.IsPrimary:
            self._clear_existing_primary(contact)

        self.db.commit()
        self.db.refresh(contact)
        return contact

    def soft_delete(self, contact: UserContact):
        contact.Active = False
        self.db.commit()

    def _clear_existing_primary(self, contact: UserContact):
        (
            self.db.query(UserContact)
            .filter(
                UserContact.UserId == contact.UserId,
                UserContact.Type == contact.Type,
                UserContact.IsPrimary == True,
                UserContact.Id != contact.Id,
                UserContact.Active == True,
            )
            .update({"IsPrimary": False})
        )