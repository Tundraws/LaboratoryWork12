from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import require_roles
from logistics_app.models import User, UserRole
from logistics_app.schemas import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin)),
) -> list[User]:
    return list(session.scalars(select(User).order_by(User.created_at.desc(), User.id.desc())))

