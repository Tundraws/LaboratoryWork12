from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.config import get_settings
from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import User, UserRole
from logistics_app.schemas import TokenResponse, UserCreate, UserRead
from logistics_app.security import create_access_token, hash_password, verify_password
from logistics_app.services.catalog import ensure_unique

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    _: User | None = Depends(require_roles(UserRole.admin)),
) -> User:
    ensure_unique(session.scalar(select(User).where(User.email == payload.email)), "Email is already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/bootstrap-admin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    admins_count = session.scalar(select(User).where(User.role == UserRole.admin).limit(1))
    if admins_count is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin already exists")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=UserRole.admin,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> TokenResponse:
    user = session.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    settings = get_settings()
    token = create_access_token(user.email, user.role.value, settings.jwt_secret, settings.access_token_expire_minutes)
    return TokenResponse(access_token=token, role=user.role)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

