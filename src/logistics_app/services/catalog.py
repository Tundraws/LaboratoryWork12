from __future__ import annotations

from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from logistics_app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def get_or_404(session: Session, model: type[ModelT], entity_id: int, name: str) -> ModelT:
    entity = session.get(model, entity_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found")
    return entity


def ensure_unique(existing: object | None, message: str) -> None:
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)

