from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from logistics_app.database import Base, get_session
from logistics_app.main import create_app


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        yield db
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def client(session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(client: TestClient, email: str = "admin@example.com", password: str = "Admin12345") -> dict[str, str]:
    response = client.post(
        "/auth/bootstrap-admin",
        json={"email": email, "full_name": "Admin User", "password": password, "role": "admin"},
    )
    assert response.status_code in {201, 403}
    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def create_route(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/routes",
        headers=headers,
        json={
            "name": "Moscow - Tver",
            "origin": "Moscow",
            "destination": "Tver",
            "distance_km": 180,
            "planned_duration_min": 210,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_driver(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/drivers",
        headers=headers,
        json={"full_name": "Ivan Driver", "license_number": "DRV00013", "phone": "+79000000013"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_vehicle(client: TestClient, headers: dict[str, str], capacity_kg: int = 10_000) -> int:
    response = client.post(
        "/vehicles",
        headers=headers,
        json={"plate_number": "А013ВС77", "model": "KAMAZ", "capacity_kg": capacity_kg},
    )
    assert response.status_code == 201
    return response.json()["id"]
