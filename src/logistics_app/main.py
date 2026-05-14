from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from logistics_app.database import init_db
from logistics_app.routers import admin, auth, drivers, orders, reports, routes, telemetry, vehicles


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Logistics Management System",
        description="REST API for routes, vehicles, drivers, delivery orders and GLONASS telemetry.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(drivers.router)
    app.include_router(vehicles.router)
    app.include_router(routes.router)
    app.include_router(orders.router)
    app.include_router(telemetry.router)
    app.include_router(reports.router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

