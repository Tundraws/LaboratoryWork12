from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import GlonassPing, User, UserRole, Vehicle
from logistics_app.schemas import GlonassPingCreate, GlonassPingRead
from logistics_app.services.catalog import get_or_404

router = APIRouter(prefix="/telemetry", tags=["glonass"])


@router.post("/glonass", response_model=GlonassPingRead, status_code=status.HTTP_201_CREATED)
def create_ping(
    payload: GlonassPingCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> GlonassPing:
    get_or_404(session, Vehicle, payload.vehicle_id, "Vehicle")
    ping = GlonassPing(**payload.model_dump(exclude_none=True))
    session.add(ping)
    session.commit()
    session.refresh(ping)
    return ping


@router.get("/vehicles/{vehicle_id}/last", response_model=GlonassPingRead)
def last_vehicle_ping(
    vehicle_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> GlonassPing:
    get_or_404(session, Vehicle, vehicle_id, "Vehicle")
    ping = session.scalar(
        select(GlonassPing).where(GlonassPing.vehicle_id == vehicle_id).order_by(GlonassPing.recorded_at.desc())
    )
    if ping is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Telemetry not found")
    return ping

