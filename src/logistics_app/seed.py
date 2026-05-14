from __future__ import annotations

from sqlalchemy import select

from logistics_app.database import SessionLocal, init_db
from logistics_app.models import Driver, Route, User, UserRole, Vehicle
from logistics_app.security import hash_password


def seed_demo_data() -> None:
    init_db()
    with SessionLocal() as session:
        if session.scalar(select(User).where(User.email == "admin@logistics.local")) is None:
            session.add(
                User(
                    email="admin@logistics.local",
                    full_name="Demo Administrator",
                    password_hash=hash_password("Admin12345"),
                    role=UserRole.admin,
                )
            )
        if session.scalar(select(Route).limit(1)) is None:
            session.add_all(
                [
                    Route(
                        name="Moscow - Kazan Express",
                        origin="Moscow",
                        destination="Kazan",
                        distance_km=820,
                        planned_duration_min=720,
                    ),
                    Route(
                        name="Moscow Warehouse Ring",
                        origin="Warehouse North",
                        destination="Warehouse South",
                        distance_km=74,
                        planned_duration_min=160,
                    ),
                ]
            )
        if session.scalar(select(Vehicle).limit(1)) is None:
            session.add_all(
                [
                    Vehicle(plate_number="А123ВС77", model="KAMAZ 5490", capacity_kg=20_000),
                    Vehicle(plate_number="М456ОР177", model="GAZon Next", capacity_kg=5_000),
                ]
            )
        if session.scalar(select(Driver).limit(1)) is None:
            session.add_all(
                [
                    Driver(full_name="Ivan Petrov", license_number="DRV202601", phone="+79001234567"),
                    Driver(full_name="Sergey Volkov", license_number="DRV202602", phone="+79007654321"),
                ]
            )
        session.commit()


if __name__ == "__main__":
    seed_demo_data()

