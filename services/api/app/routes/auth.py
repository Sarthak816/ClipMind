import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.session import Session as SessionModel
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, UserResponse, TokenResponse
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _issue_tokens(user: User, db: Session) -> TokenResponse:
    access = create_access_token(str(user.id), user.role)
    refresh = create_refresh_token(str(user.id))
    refresh_hash = _hash_token(refresh)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TTL_DAYS
    )
    db_session = SessionModel(
        user_id=user.id, refresh_token_hash=refresh_hash, expires_at=expires_at
    )
    db.add(db_session)
    db.commit()
    return TokenResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            displayName=user.display_name,
            role=user.role,
            status=user.status,
        ),
        accessToken=access,
    )


def _set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TTL_DAYS * 86400,
        path="/",
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserRegister, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.displayName,
        role="learner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    tokens = _issue_tokens(user, db)
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))
    return tokens


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended"
        )
    tokens = _issue_tokens(user, db)
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    cookie = request.cookies.get("refresh_token")
    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token"
        )
    payload = decode_token(cookie)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    db_session = (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == payload["sub"],
            SessionModel.refresh_token_hash == _hash_token(cookie),
            SessionModel.revoked_at.is_(None),
        )
        .first()
    )
    if not db_session or db_session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        )
    db_session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    tokens = _issue_tokens(user, db)
    _set_refresh_cookie(response, create_refresh_token(str(user.id)))
    return tokens


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    cookie = request.cookies.get("refresh_token")
    if cookie:
        payload = decode_token(cookie)
        if payload:
            db.query(SessionModel).filter(
                SessionModel.user_id == payload["sub"],
                SessionModel.refresh_token_hash == _hash_token(cookie),
            ).update({"revoked_at": datetime.now(timezone.utc)})
            db.commit()
    response.delete_cookie("refresh_token", path="/")
    return None


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        displayName=user.display_name,
        role=user.role,
        status=user.status,
    )
