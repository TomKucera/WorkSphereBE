from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.repositories.user_contact_repository import UserContactRepository
from app.core.auth import get_current_user
from app.schemas.users.user_contact import (
    UserContactCreate,
    UserContactUpdate,
    UserContactResponse,
)

router = APIRouter(prefix="/contacts", tags=["User Contacts"])


@router.get("", response_model=list[UserContactResponse])
def list_contacts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = UserContactRepository(db)
    return repo.list_by_user(current_user)


@router.post("", response_model=UserContactResponse)
def create_contact(
    data: UserContactCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = UserContactRepository(db)

    contact = repo.create(
        UserId=current_user,
        Type=data.Type,
        Value=data.Value,
        IsPrimary=data.IsPrimary,
    )

    return contact


@router.put("/{contact_id}", response_model=UserContactResponse)
def update_contact(
    contact_id: int,
    data: UserContactUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = UserContactRepository(db)

    contact = repo.get(contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = data.model_dump(exclude_unset=True)

    updated = repo.update(contact, **update_data)
    return updated


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = UserContactRepository(db)

    contact = repo.get(contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    repo.soft_delete(contact)
    return {"success": True}
