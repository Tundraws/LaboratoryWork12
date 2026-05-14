from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from logistics_app.models import DeliveryOrder, GlonassPing, OrderStatus, Route, Vehicle, VehicleStatus
from logistics_app.schemas import DashboardReport, RouteProfitability


def dashboard(session: Session) -> DashboardReport:
    total_orders = session.scalar(select(func.count(DeliveryOrder.id))) or 0
    delivered_orders = (
        session.scalar(select(func.count(DeliveryOrder.id)).where(DeliveryOrder.status == OrderStatus.delivered)) or 0
    )
    active_orders = (
        session.scalar(
            select(func.count(DeliveryOrder.id)).where(
                DeliveryOrder.status.in_([OrderStatus.planned, OrderStatus.in_transit])
            )
        )
        or 0
    )
    total_vehicles = session.scalar(select(func.count(Vehicle.id))) or 0
    assigned_vehicles = (
        session.scalar(select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.assigned)) or 0
    )
    average_speed = session.scalar(select(func.avg(GlonassPing.speed_kmh))) or 0.0
    utilization = round((assigned_vehicles / total_vehicles * 100), 2) if total_vehicles else 0.0
    return DashboardReport(
        total_orders=total_orders,
        active_orders=active_orders,
        delivered_orders=delivered_orders,
        fleet_utilization_percent=utilization,
        average_vehicle_speed_kmh=round(float(average_speed), 2),
    )


def route_profitability(session: Session) -> list[RouteProfitability]:
    rows = session.execute(
        select(
            Route.id,
            Route.name,
            func.count(DeliveryOrder.id),
            func.coalesce(func.sum(DeliveryOrder.weight_kg), 0),
            func.coalesce(func.sum(DeliveryOrder.weight_kg * Route.distance_km * 0.035), 0.0),
        )
        .join(DeliveryOrder, DeliveryOrder.route_id == Route.id, isouter=True)
        .group_by(Route.id, Route.name)
        .order_by(func.count(DeliveryOrder.id).desc(), Route.name.asc())
    ).all()
    return [
        RouteProfitability(
            route_id=row[0],
            route_name=row[1],
            orders_count=row[2],
            total_weight_kg=row[3],
            estimated_revenue=round(float(row[4]), 2),
        )
        for row in rows
    ]
