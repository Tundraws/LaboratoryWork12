from __future__ import annotations

from fastapi.testclient import TestClient
from tests.conftest import auth_headers


def test_bootstrap_login_and_me(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert response.json()["role"] == "admin"


def test_login_rejects_wrong_password(client: TestClient) -> None:
    auth_headers(client)
    response = client.post("/auth/login", data={"username": "admin@example.com", "password": "bad-pass"})
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client: TestClient) -> None:
    response = client.get("/drivers")
    assert response.status_code == 401


def test_viewer_cannot_create_vehicle(client: TestClient) -> None:
    headers = auth_headers(client)
    created = client.post(
        "/auth/register",
        headers=headers,
        json={"email": "viewer@example.com", "full_name": "View Only", "password": "Viewer123", "role": "viewer"},
    )
    assert created.status_code == 201
    login = client.post("/auth/login", data={"username": "viewer@example.com", "password": "Viewer123"})
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.post(
        "/vehicles",
        headers=viewer_headers,
        json={"plate_number": "В777ЕН77", "model": "Van", "capacity_kg": 1500},
    )
    assert response.status_code == 403

