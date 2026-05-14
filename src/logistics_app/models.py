from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from logistics_app.database import Base


class UserRole(str, Enum):
    admin = "admin"
    dispatcher = "dispatcher"
    viewer = "viewer"


class VehicleStatus(str, Enum):
    available = "available"
    assigned = "assigned"
    maintenance = "maintenance"


class DriverStatus(str, Enum):
    available = "available"
    on_route = "on_route"
    suspended = "suspended"


class OrderStatus(str, Enum):
    new = "new"
    planned = "planned"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.dispatcher)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    license_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(32))
    status: Mapped[DriverStatus] = mapped_column(SAEnum(DriverStatus), default=DriverStatus.available)
    orders: Mapped[list["DeliveryOrder"]] = relationship(back_populates="driver")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    model: Mapped[str] = mapped_column(String(120))
    capacity_kg: Mapped[int] = mapped_column(Integer)
    status: Mapped[VehicleStatus] = mapped_column(SAEnum(VehicleStatus), default=VehicleStatus.available)
    orders: Mapped[list["DeliveryOrder"]] = relationship(back_populates="vehicle")
    telemetry: Mapped[list["GlonassPing"]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    origin: Mapped[str] = mapped_column(String(160))
    destination: Mapped[str] = mapped_column(String(160))
    distance_km: Mapped[float] = mapped_column(Float)
    planned_duration_min: Mapped[int] = mapped_column(Integer)
    orders: Mapped[list["DeliveryOrder"]] = relationship(back_populates="route")


class DeliveryOrder(Base):
    __tablename__ = "delivery_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cargo_name: Mapped[str] = mapped_column(String(180), index=True)
    weight_kg: Mapped[int] = mapped_column(Integer)
    customer_name: Mapped[str] = mapped_column(String(180), index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicles.id"), nullable=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.new, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    route: Mapped[Route] = relationship(back_populates="orders")
    vehicle: Mapped[Vehicle | None] = relationship(back_populates="orders")
    driver: Mapped[Driver | None] = relationship(back_populates="orders")


class GlonassPing(Base):
    __tablename__ = "glonass_pings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed_kmh: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    vehicle: Mapped[Vehicle] = relationship(back_populates="telemetry")

