from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session

from app.features.dashboard.repositories.inventory_health import (
    InventoryHealthRepository,
)
from app.features.dashboard.repositories.material_coverage import (
    MaterialCoverageRepository,
)
from app.features.dashboard.repositories.operational_health import (
    OperationalHealthRepository,
)
from app.features.dashboard.repositories.procurement import (
    ProcurementRepository,
)
from app.features.dashboard.repositories.supplier_risk import (
    SupplierRiskRepository,
)
from app.features.dashboard.repositories.production_readiness import (
    ProductionReadinessRepository,
)

async def get_operational_health_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> OperationalHealthRepository:

    return OperationalHealthRepository(session)

async def get_inventory_health_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> InventoryHealthRepository:

    return InventoryHealthRepository(session)

async def get_material_coverage_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> MaterialCoverageRepository:

    return MaterialCoverageRepository(session)

async def get_procurement_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ProcurementRepository:

    return ProcurementRepository(session)

async def get_supplier_risk_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> SupplierRiskRepository:

    return SupplierRiskRepository(session)

def get_production_readiness_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_db_session),
    ],
) -> ProductionReadinessRepository:

    return ProductionReadinessRepository(session)