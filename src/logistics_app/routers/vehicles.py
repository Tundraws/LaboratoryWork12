from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import User, UserRole, Vehicle
from logistics_app.schemas import ApiMessage, VehicleCreate, VehicleRead, VehicleUpdate
from logistics_app.services.catalog import ensure_unique, get_or_404

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleRead])
def list_vehicles(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> list[Vehicle]:
    return list(session.scalars(select(Vehicle).order_by(Vehicle.plate_number)))


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Vehicle:
    ensure_unique(
        session.scalar(select(Vehicle).where(Vehicle.plate_number == payload.plate_number)),
        "Vehicle plate already exists",
    )
    vehicle = Vehicle(**payload.model_dump())
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> Vehicle:
    return get_or_404(session, Vehicle, vehicle_id, "Vehicle")


@router.put("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Vehicle:
    vehicle = get_or_404(session, Vehicle, vehicle_id, "Vehicle")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", response_model=ApiMessage)
def delete_vehicle(
    vehicle_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin)),
) -> ApiMessage:
    vehicle = get_or_404(session, Vehicle, vehicle_id, "Vehicle")
    session.delete(vehicle)
    session.commit()
    return ApiMessage(detail="Vehicle deleted")

