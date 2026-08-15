from typing import Annotated

from fastapi import Depends

from app.features.dashboard.dependencies.repository import (
    get_inventory_health_repository,
    get_material_coverage_repository,
    get_operational_health_repository,
    get_procurement_repository,
    get_supplier_risk_repository,
)

from app.features.dashboard.logic.inventory_health import (
    InventoryHealthLogic,
)
from app.features.dashboard.logic.material_coverage import (
    MaterialCoverageLogic,
)
from app.features.dashboard.logic.operational_health import (
    OperationalHealthLogic,
)
from app.features.dashboard.logic.procurement import (
    ProcurementLogic,
)
from app.features.dashboard.logic.production_readiness import (
    ProductionReadinessLogic,
)
from app.features.dashboard.logic.production_risks import (
    ProductionRisksLogic,
)
from app.features.dashboard.logic.supplier_risk import (
    SupplierRiskLogic,
)

from app.features.dashboard.dependencies.repository import (
    get_production_readiness_repository,
)

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

def get_operational_health_logic(
    repository: Annotated[
        OperationalHealthRepository,
        Depends(get_operational_health_repository),
    ],
) -> OperationalHealthLogic:

    return OperationalHealthLogic(
        repository=repository,
    )

def get_inventory_health_logic(
    repository: Annotated[
        InventoryHealthRepository,
        Depends(get_inventory_health_repository),
    ],
) -> InventoryHealthLogic:

    return InventoryHealthLogic(
        repository=repository,
    )

def get_material_coverage_logic(
    repository: Annotated[
        MaterialCoverageRepository,
        Depends(get_material_coverage_repository),
    ],
) -> MaterialCoverageLogic:

    return MaterialCoverageLogic(
        repository=repository,
    )

def get_procurement_logic(
    repository: Annotated[
        ProcurementRepository,
        Depends(get_procurement_repository),
    ],
) -> ProcurementLogic:

    return ProcurementLogic(
        repository=repository,
    )

def get_supplier_risk_logic(

) -> SupplierRiskLogic:

    return SupplierRiskLogic(
    )

def get_production_readiness_logic(
    repository: Annotated[
        ProductionReadinessRepository,
        Depends(get_production_readiness_repository),
    ],
) -> ProductionReadinessLogic:

    return ProductionReadinessLogic(
        repository=repository,
    )

def get_production_risks_logic() -> ProductionRisksLogic:

    return ProductionRisksLogic()