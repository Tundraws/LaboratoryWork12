from __future__ import annotations

from fastapi.testclient import TestClient
from tests.conftest import auth_headers, create_driver, create_route, create_vehicle


def test_order_crud_assignment_and_reports(client: TestClient) -> None:
    headers = auth_headers(client)
    route_id = create_route(client, headers)
    driver_id = create_driver(client, headers)
    vehicle_id = create_vehicle(client, headers)

    created = client.post(
        "/orders",
        headers=headers,
        json={
            "cargo_name": "Medical equipment",
            "weight_kg": 1200,
            "customer_name": "Clinic Partner",
            "route_id": route_id,
            "notes": "Fragile cargo",
        },
    )
    assert created.status_code == 201
    order_id = created.json()["id"]
    assert created.json()["status"] == "new"

    assigned = client.post(
        f"/orders/{order_id}/assign",
        headers=headers,
        json={"driver_id": driver_id, "vehicle_id": vehicle_id},
    )
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "planned"

    delivered = client.put(f"/orders/{order_id}", headers=headers, json={"status": "delivered"})
    assert delivered.status_code == 200
    assert delivered.json()["delivered_at"] is not None

    ping = client.post(
        "/telemetry/glonass",
        headers=headers,
        json={"vehicle_id": vehicle_id, "latitude": 55.75, "longitude": 37.61, "speed_kmh": 67.5},
    )
    assert ping.status_code == 201
    last_ping = client.get(f"/telemetry/vehicles/{vehicle_id}/last", headers=headers)
    assert last_ping.status_code == 200
    assert last_ping.json()["speed_kmh"] == 67.5

    dashboard = client.get("/reports/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_orders"] == 1
    assert dashboard.json()["delivered_orders"] == 1

    profitability = client.get("/reports/routes/profitability", headers=headers)
    assert profitability.status_code == 200
    assert profitability.json()[0]["orders_count"] == 1


def test_order_rejects_overloaded_vehicle(client: TestClient) -> None:
    headers = auth_headers(client)
    route_id = create_route(client, headers)
    vehicle_id = create_vehicle(client, headers, capacity_kg=500)
    response = client.post(
        "/orders",
        headers=headers,
        json={
            "cargo_name": "Steel beams",
            "weight_kg": 900,
            "customer_name": "Plant",
            "route_id": route_id,
            "vehicle_id": vehicle_id,
        },
    )
    assert response.status_code == 422
    assert "capacity" in response.json()["detail"]


def test_missing_entities_return_404(client: TestClient) -> None:
    headers = auth_headers(client)
    assert client.get("/orders/999", headers=headers).status_code == 404
    assert client.get("/telemetry/vehicles/999/last", headers=headers).status_code == 404


def test_validation_rejects_invalid_plate_and_coordinates(client: TestClient) -> None:
    headers = auth_headers(client)
    bad_vehicle = client.post(
        "/vehicles",
        headers=headers,
        json={"plate_number": "bad-plate", "model": "Truck", "capacity_kg": 1000},
    )
    assert bad_vehicle.status_code == 422

    bad_ping = client.post(
        "/telemetry/glonass",
        headers=headers,
        json={"vehicle_id": 1, "latitude": 120, "longitude": 37.61, "speed_kmh": 12},
    )
    assert bad_ping.status_code == 422


def test_catalog_crud_and_admin_user_list(client: TestClient) -> None:
    headers = auth_headers(client)
    route_id = create_route(client, headers)
    driver_id = create_driver(client, headers)
    vehicle_id = create_vehicle(client, headers)

    users = client.get("/admin/users", headers=headers)
    assert users.status_code == 200
    assert users.json()[0]["email"] == "admin@example.com"

    assert client.get("/routes", headers=headers).status_code == 200
    assert client.get(f"/routes/{route_id}", headers=headers).json()["name"] == "Moscow - Tver"
    updated_route = client.put(f"/routes/{route_id}", headers=headers, json={"planned_duration_min": 240})
    assert updated_route.status_code == 200
    assert updated_route.json()["planned_duration_min"] == 240

    assert client.get("/drivers", headers=headers).status_code == 200
    updated_driver = client.put(f"/drivers/{driver_id}", headers=headers, json={"status": "suspended"})
    assert updated_driver.status_code == 200
    assert updated_driver.json()["status"] == "suspended"

    assert client.get("/vehicles", headers=headers).status_code == 200
    updated_vehicle = client.put(f"/vehicles/{vehicle_id}", headers=headers, json={"status": "maintenance"})
    assert updated_vehicle.status_code == 200
    assert updated_vehicle.json()["status"] == "maintenance"

    assert client.delete(f"/drivers/{driver_id}", headers=headers).status_code == 200
    assert client.delete(f"/vehicles/{vehicle_id}", headers=headers).status_code == 200
    assert client.delete(f"/routes/{route_id}", headers=headers).status_code == 200


def test_order_delete_and_assignment_reject_suspended_driver(client: TestClient) -> None:
    headers = auth_headers(client)
    route_id = create_route(client, headers)
    driver_id = create_driver(client, headers)
    vehicle_id = create_vehicle(client, headers)
    client.put(f"/drivers/{driver_id}", headers=headers, json={"status": "suspended"})
    created = client.post(
        "/orders",
        headers=headers,
        json={"cargo_name": "Boxes", "weight_kg": 100, "customer_name": "Retail", "route_id": route_id},
    )
    order_id = created.json()["id"]

    rejected = client.post(
        f"/orders/{order_id}/assign",
        headers=headers,
        json={"driver_id": driver_id, "vehicle_id": vehicle_id},
    )
    assert rejected.status_code == 422
    assert "suspended" in rejected.json()["detail"]

    deleted = client.delete(f"/orders/{order_id}", headers=headers)
    assert deleted.status_code == 200
    assert client.get(f"/orders/{order_id}", headers=headers).status_code == 404
