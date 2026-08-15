from typing import Annotated

from fastapi import APIRouter, Depends

from app.features.dashboard.schema import (
    DashboardOverviewResponse,
)
from app.features.dashboard.service import (
    DashboardOverviewService,
)
from app.features.dashboard.dependencies.service import (
    get_dashboard_overview_service,
)


dashboard_route = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@dashboard_route.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
async def get_dashboard_overview(
    service: Annotated[
        DashboardOverviewService,
        Depends(get_dashboard_overview_service),
    ],
) -> DashboardOverviewResponse:

    return await service.execute()