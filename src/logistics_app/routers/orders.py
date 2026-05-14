from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user, require_roles
from logistics_app.models import DeliveryOrder, User, UserRole
from logistics_app.schemas import ApiMessage, AssignmentRequest, OrderCreate, OrderRead, OrderUpdate
from logistics_app.services.catalog import get_or_404
from logistics_app.services.orders import assign_order, create_order, delete_order, update_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
def list_orders(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> list[DeliveryOrder]:
    statement = select(DeliveryOrder).order_by(DeliveryOrder.created_at.desc(), DeliveryOrder.id.desc())
    return list(session.scalars(statement))


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_delivery_order(
    payload: OrderCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> DeliveryOrder:
    return create_order(session, payload)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> DeliveryOrder:
    return get_or_404(session, DeliveryOrder, order_id, "Order")


@router.put("/{order_id}", response_model=OrderRead)
def edit_order(
    order_id: int,
    payload: OrderUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> DeliveryOrder:
    return update_order(session, order_id, payload)


@router.post("/{order_id}/assign", response_model=OrderRead)
def assign_delivery_order(
    order_id: int,
    payload: AssignmentRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin, UserRole.dispatcher)),
) -> DeliveryOrder:
    return assign_order(session, order_id, payload)


@router.delete("/{order_id}", response_model=ApiMessage)
def remove_order(
    order_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_roles(UserRole.admin)),
) -> ApiMessage:
    delete_order(session, order_id)
    return ApiMessage(detail="Order deleted")
