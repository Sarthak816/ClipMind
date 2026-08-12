import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/me", tags=["me"])


class ProfileUpdate(BaseModel):
    displayName: str | None = None


class PasswordChange(BaseModel):
    currentPassword: str
    newPassword: str


@router.get("")
def get_profile(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "displayName": user.display_name,
        "role": user.role,
        "status": user.status,
    }


@router.patch("")
def update_profile(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.displayName is not None:
        user.display_name = body.displayName
    db.commit()
    db.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "displayName": user.display_name,
        "role": user.role,
        "status": user.status,
    }


@router.post("/change-password")
def change_password(
    body: PasswordChange,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.currentPassword, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(body.newPassword)
    db.commit()
    return {"message": "Password updated"}
