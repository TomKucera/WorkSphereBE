from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.repositories.user_repository import UserRepository

ADMIN_USER_DATA = {
    "Login": "admin",
    # "PasswordHash": hash_password("3402"),
    "FirstName": "Admin",
    "LastName": "User",
    "Active": True,
}

def seed_admin(db: Session):
    repo = UserRepository(db)

    print("Seeding admin user...")

    user_data = ADMIN_USER_DATA.copy()
    user_data["PasswordHash"] = hash_password("3402")

    try:
        return repo.create(**user_data)
    except IntegrityError:
        db.rollback()
        return repo.get_by_login(ADMIN_USER_DATA["Login"])
