from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from logistics_app.database import get_session
from logistics_app.dependencies import get_current_user
from logistics_app.models import User
from logistics_app.schemas import DashboardReport, RouteProfitability
from logistics_app.services.reports import dashboard, route_profitability

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardReport)
def dashboard_report(session: Session = Depends(get_session), _: User = Depends(get_current_user)) -> DashboardReport:
    return dashboard(session)


@router.get("/routes/profitability", response_model=list[RouteProfitability])
def route_profitability_report(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[RouteProfitability]:
    return route_profitability(session)

