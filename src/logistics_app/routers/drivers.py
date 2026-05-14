from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import Driver, User, UserRole
from logistics_app.schemas import ApiMessage, DriverCreate, DriverRead, DriverUpdate
from logistics_app.services.catalog import ensure_unique, get_or_404

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverRead])
def list_drivers(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> list[Driver]:
    return list(session.scalars(select(Driver).order_by(Driver.full_name)))


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Driver:
    ensure_unique(
        session.scalar(select(Driver).where(Driver.license_number == payload.license_number)),
        "Driver license already exists",
    )
    driver = Driver(**payload.model_dump())
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> Driver:
    return get_or_404(session, Driver, driver_id, "Driver")


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Driver:
    driver = get_or_404(session, Driver, driver_id, "Driver")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    session.commit()
    session.refresh(driver)
    return driver


@router.delete("/{driver_id}", response_model=ApiMessage)
def delete_driver(
    driver_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin)),
) -> ApiMessage:
    driver = get_or_404(session, Driver, driver_id, "Driver")
    session.delete(driver)
    session.commit()
    return ApiMessage(detail="Driver deleted")

