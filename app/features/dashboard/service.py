from app.features.dashboard.schema import (
    DashboardOverviewResponse,
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


class DashboardOverviewService:

    def __init__(
        self,
        production_risk_analyzer: ProductionRiskAnalyzer,
        operational_health: OperationalHealthLogic,
        production_readiness: ProductionReadinessLogic,
        inventory_health: InventoryHealthLogic,
        procurement: ProcurementLogic,
        production_risks: ProductionRisksLogic,
        material_coverage: MaterialCoverageLogic,
        supplier_risk: SupplierRiskLogic,
    ):
        self.production_risk_analyzer = (
            production_risk_analyzer
        )

        self.operational_health = operational_health
        self.production_readiness = production_readiness
        self.inventory_health = inventory_health
        self.procurement = procurement
        self.production_risks = production_risks
        self.material_coverage = material_coverage
        self.supplier_risk = supplier_risk

    async def execute(
        self,
    ) -> DashboardOverviewResponse:

        production_analysis = (
            await self.production_risk_analyzer.execute()
        )

        operational_health = (
            await self.operational_health.get(
                production_analysis,
            )
        )

        production_readiness = (
            await self.production_readiness.get(
                production_analysis,
            )
        )

        inventory_health = (
            await self.inventory_health.get()
        )

        procurement = (
            await self.procurement.get(
                production_analysis,
            )
        )

        production_risks = (
            await self.production_risks.get(
                production_analysis,
            )
        )

        material_coverage = (
            await self.material_coverage.execute()
        )

        supplier_risk = (
            await self.supplier_risk.get(
                production_analysis,
            )
        )

        return DashboardOverviewResponse(
            operational_health=operational_health,
            production_readiness=production_readiness,
            inventory_health=inventory_health,
            procurement=procurement,
            production_risks=production_risks,
            material_coverage=material_coverage,
            supplier_risk=supplier_risk,
        )