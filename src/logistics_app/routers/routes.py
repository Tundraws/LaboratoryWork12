from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import Route, User, UserRole
from logistics_app.schemas import ApiMessage, RouteCreate, RouteRead, RouteUpdate
from logistics_app.services.catalog import get_or_404

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[RouteRead])
def list_routes(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> list[Route]:
    return list(session.scalars(select(Route).order_by(Route.name)))


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route(
    payload: RouteCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Route:
    route = Route(**payload.model_dump())
    session.add(route)
    session.commit()
    session.refresh(route)
    return route


@router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> Route:
    return get_or_404(session, Route, route_id, "Route")


@router.put("/{route_id}", response_model=RouteRead)
def update_route(
    route_id: int,
    payload: RouteUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> Route:
    route = get_or_404(session, Route, route_id, "Route")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(route, field, value)
    session.commit()
    session.refresh(route)
    return route


@router.delete("/{route_id}", response_model=ApiMessage)
def delete_route(
    route_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin)),
) -> ApiMessage:
    route = get_or_404(session, Route, route_id, "Route")
    session.delete(route)
    session.commit()
    return ApiMessage(detail="Route deleted")

