from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from logistics_app.models import DriverStatus, OrderStatus, UserRole, VehicleStatus


class ApiMessage(BaseModel):
    detail: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.dispatcher


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class DriverCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=255)
    license_number: str = Field(pattern=r"^[A-Z0-9]{6,16}$")
    phone: str = Field(pattern=r"^\+?[0-9]{10,15}$")
    status: DriverStatus = DriverStatus.available


class DriverUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=255)
    phone: str | None = Field(default=None, pattern=r"^\+?[0-9]{10,15}$")
    status: DriverStatus | None = None


class DriverRead(DriverCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class VehicleCreate(BaseModel):
    plate_number: str = Field(pattern=r"^[АВЕКМНОРСТУХABEKMHOPCTYX]\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$")
    model: str = Field(min_length=2, max_length=120)
    capacity_kg: int = Field(gt=0, le=40_000)
    status: VehicleStatus = VehicleStatus.available


class VehicleUpdate(BaseModel):
    model: str | None = Field(default=None, min_length=2, max_length=120)
    capacity_kg: int | None = Field(default=None, gt=0, le=40_000)
    status: VehicleStatus | None = None


class VehicleRead(VehicleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RouteCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    origin: str = Field(min_length=2, max_length=160)
    destination: str = Field(min_length=2, max_length=160)
    distance_km: float = Field(gt=0, le=20_000)
    planned_duration_min: int = Field(gt=0, le=30_000)


class RouteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=160)
    origin: str | None = Field(default=None, min_length=2, max_length=160)
    destination: str | None = Field(default=None, min_length=2, max_length=160)
    distance_km: float | None = Field(default=None, gt=0, le=20_000)
    planned_duration_min: int | None = Field(default=None, gt=0, le=30_000)


class RouteRead(RouteCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    cargo_name: str = Field(min_length=2, max_length=180)
    weight_kg: int = Field(gt=0, le=40_000)
    customer_name: str = Field(min_length=2, max_length=180)
    route_id: int = Field(gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    driver_id: int | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=1500)


class OrderUpdate(BaseModel):
    cargo_name: str | None = Field(default=None, min_length=2, max_length=180)
    weight_kg: int | None = Field(default=None, gt=0, le=40_000)
    customer_name: str | None = Field(default=None, min_length=2, max_length=180)
    route_id: int | None = Field(default=None, gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    driver_id: int | None = Field(default=None, gt=0)
    status: OrderStatus | None = None
    notes: str | None = Field(default=None, max_length=1500)


class OrderRead(BaseModel):
    id: int
    cargo_name: str
    weight_kg: int
    customer_name: str
    route_id: int
    vehicle_id: int | None
    driver_id: int | None
    status: OrderStatus
    notes: str | None
    created_at: datetime
    delivered_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class GlonassPingCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kmh: float = Field(ge=0, le=180)
    recorded_at: datetime | None = None


class GlonassPingRead(BaseModel):
    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardReport(BaseModel):
    total_orders: int
    active_orders: int
    delivered_orders: int
    fleet_utilization_percent: float
    average_vehicle_speed_kmh: float


class AssignmentRequest(BaseModel):
    driver_id: int = Field(gt=0)
    vehicle_id: int = Field(gt=0)


class RouteProfitability(BaseModel):
    route_id: int
    route_name: str
    orders_count: int
    total_weight_kg: int
    estimated_revenue: float


class CodeReviewItem(BaseModel):
    generated_by_ai: str
    problem: str
    fixed_by_student: str

