from sqlalchemy.orm import Session
from app.db.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self):
        return (
            self.db.query(User)
            .filter(User.Active == True)
            .order_by(User.CreatedAt.desc())
            .all()
        )

    def get(self, user_id: int):
        return (
            self.db.query(User)
            .filter(User.Id == user_id, User.Active == True)
            .first()
        )

    def get_by_login(self, login: str):
        return (
            self.db.query(User)
            .filter(User.Login == login, User.Active == True)
            .first()
        )

    def create(self, **kwargs):
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **kwargs):
        for k, v in kwargs.items():
            setattr(user, k, v)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User):
        user.Active = False
        self.db.commit()