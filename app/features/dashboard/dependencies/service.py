from typing import Annotated

from fastapi import Depends

from app.features.dashboard.dependencies.logic import (
    get_inventory_health_logic,
    get_material_coverage_logic,
    get_operational_health_logic,
    get_procurement_logic,
    get_production_readiness_logic,
    get_production_risks_logic,
    get_supplier_risk_logic,
)

from app.features.dashboard.service import (
    DashboardOverviewService,
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

from app.features.production_risk.analyzer.production_risk import (
    ProductionRiskAnalyzer,
)

from app.features.production_risk.dependencies.analyzers import (
    get_production_risk_analyzer,
)

def get_dashboard_overview_service(
    production_risk_analyzer: Annotated[
        ProductionRiskAnalyzer,
        Depends(get_production_risk_analyzer),
    ],
    operational_health: Annotated[
        OperationalHealthLogic,
        Depends(get_operational_health_logic),
    ],
    production_readiness: Annotated[
        ProductionReadinessLogic,
        Depends(get_production_readiness_logic),
    ],
    inventory_health: Annotated[
        InventoryHealthLogic,
        Depends(get_inventory_health_logic),
    ],
    procurement: Annotated[
        ProcurementLogic,
        Depends(get_procurement_logic),
    ],
    production_risks: Annotated[
        ProductionRisksLogic,
        Depends(get_production_risks_logic),
    ],
    material_coverage: Annotated[
        MaterialCoverageLogic,
        Depends(get_material_coverage_logic),
    ],
    supplier_risk: Annotated[
        SupplierRiskLogic,
        Depends(get_supplier_risk_logic),
    ],
) -> DashboardOverviewService:

    return DashboardOverviewService(
        production_risk_analyzer=production_risk_analyzer,
        operational_health=operational_health,
        production_readiness=production_readiness,
        inventory_health=inventory_health,
        procurement=procurement,
        production_risks=production_risks,
        material_coverage=material_coverage,
        supplier_risk=supplier_risk,
    )