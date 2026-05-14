from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from logistics_app.models import DeliveryOrder, Driver, DriverStatus, OrderStatus, Route, Vehicle, VehicleStatus
from logistics_app.schemas import AssignmentRequest, OrderCreate, OrderUpdate
from logistics_app.services.catalog import get_or_404


def create_order(session: Session, payload: OrderCreate) -> DeliveryOrder:
    route = get_or_404(session, Route, payload.route_id, "Route")
    vehicle = session.get(Vehicle, payload.vehicle_id) if payload.vehicle_id else None
    driver = session.get(Driver, payload.driver_id) if payload.driver_id else None
    if payload.vehicle_id and vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    if payload.driver_id and driver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    if vehicle and payload.weight_kg > vehicle.capacity_kg:
        raise HTTPException(status_code=422, detail="Cargo exceeds vehicle capacity")

    order = DeliveryOrder(
        cargo_name=payload.cargo_name,
        weight_kg=payload.weight_kg,
        customer_name=payload.customer_name,
        route_id=route.id,
        vehicle_id=vehicle.id if vehicle else None,
        driver_id=driver.id if driver else None,
        status=OrderStatus.planned if vehicle and driver else OrderStatus.new,
        notes=payload.notes,
    )
    session.add(order)
    _reserve_resources(vehicle, driver)
    session.commit()
    session.refresh(order)
    return order


def update_order(session: Session, order_id: int, payload: OrderUpdate) -> DeliveryOrder:
    order = get_or_404(session, DeliveryOrder, order_id, "Order")
    data = payload.model_dump(exclude_unset=True)
    if "route_id" in data:
        get_or_404(session, Route, data["route_id"], "Route")
    if "vehicle_id" in data and data["vehicle_id"] is not None:
        vehicle = get_or_404(session, Vehicle, data["vehicle_id"], "Vehicle")
        new_weight = data.get("weight_kg", order.weight_kg)
        if new_weight > vehicle.capacity_kg:
            raise HTTPException(status_code=422, detail="Cargo exceeds vehicle capacity")
    if "driver_id" in data and data["driver_id"] is not None:
        get_or_404(session, Driver, data["driver_id"], "Driver")
    if data.get("status") == OrderStatus.delivered:
        data["delivered_at"] = datetime.now(UTC).replace(tzinfo=None)
    for field, value in data.items():
        setattr(order, field, value)
    session.commit()
    session.refresh(order)
    return order


def assign_order(session: Session, order_id: int, payload: AssignmentRequest) -> DeliveryOrder:
    order = get_or_404(session, DeliveryOrder, order_id, "Order")
    driver = get_or_404(session, Driver, payload.driver_id, "Driver")
    vehicle = get_or_404(session, Vehicle, payload.vehicle_id, "Vehicle")
    if driver.status == DriverStatus.suspended:
        raise HTTPException(status_code=422, detail="Driver is suspended")
    if vehicle.status == VehicleStatus.maintenance:
        raise HTTPException(status_code=422, detail="Vehicle is under maintenance")
    if order.weight_kg > vehicle.capacity_kg:
        raise HTTPException(status_code=422, detail="Cargo exceeds vehicle capacity")
    order.driver_id = driver.id
    order.vehicle_id = vehicle.id
    order.status = OrderStatus.planned
    _reserve_resources(vehicle, driver)
    session.commit()
    session.refresh(order)
    return order


def delete_order(session: Session, order_id: int) -> None:
    order = get_or_404(session, DeliveryOrder, order_id, "Order")
    session.delete(order)
    session.commit()


def _reserve_resources(vehicle: Vehicle | None, driver: Driver | None) -> None:
    if vehicle is not None and vehicle.status == VehicleStatus.available:
        vehicle.status = VehicleStatus.assigned
    if driver is not None and driver.status == DriverStatus.available:
        driver.status = DriverStatus.on_route
