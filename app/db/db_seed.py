from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.repositories.user_repository import UserRepository


USERS_DATA = [
    {
        "Login": "tester",
        "Password": "WS_2043",
        "FirstName": "John",
        "LastName": "Testator",
        "Active": True,
    },
    {
        "Login": "thomas",
        "Password": "WS_3402",
        "FirstName": "Tomáš",
        "LastName": "Kučera",
        "Active": True,
    },
]


def seed_users(db: Session):
    repo = UserRepository(db)

    print("Seeding users...")

    created_users = []

    for user_data in USERS_DATA:
        data = user_data.copy()
        data["PasswordHash"] = hash_password(data.pop("Password"))

        try:
            user = repo.create(**data)
        except IntegrityError:
            db.rollback()
            user = repo.get_by_login(data["Login"])

        created_users.append(user)

    return created_users