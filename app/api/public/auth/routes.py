# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# from app.core.security import create_access_token

# router = APIRouter(prefix="/auth", tags=["Auth"])


# class LoginRequest(BaseModel):
#     username: str
#     password: str


# @router.post("/login")
# def login(data: LoginRequest):
#     # DEMO – natvrdo user
#     if data.username != "admin" or data.password != "3402":
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": data.username})
#     return {"access_token": token, "token_type": "bearer"}


from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.deps import get_db
from app.db.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)

    user = user_repo.get_by_login(data.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.PasswordHash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.Active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_access_token(
        {
            "sub": str(user.Id),
            "login": user.Login,
            "name": user.display_name,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }