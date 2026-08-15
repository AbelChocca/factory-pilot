from dataclasses import dataclass, field
from uuid import UUID

from app.features.dashboard.schema import (
    SupplierRiskOverviewItem,
    SupplierRiskSummary,
)
from app.features.dashboard.types import RiskLevel
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
)


@dataclass
class _SupplierRiskData:
    supplier_id: UUID
    supplier_name: str
    lead_time_days: int

    affected_materials: set[UUID] = field(
        default_factory=set,
    )
    critical_materials: set[UUID] = field(
        default_factory=set,
    )
    high_risk_materials: set[UUID] = field(
        default_factory=set,
    )


class SupplierRiskLogic:

    MAX_TOP_RISKS = 5

    async def get(
        self,
        production_analysis: ProductionRiskAnalysisSchema,
    ) -> SupplierRiskSummary:

        suppliers = self._collect_suppliers(
            production_analysis,
        )

        risks = [
            self._build_supplier_risk(
                supplier,
            )
            for supplier in suppliers.values()
        ]

        risks.sort(
            key=self._risk_sort_key,
        )

        return SupplierRiskSummary(
            total_suppliers=len(risks),
            suppliers_at_risk=sum(
                risk.risk_level != RiskLevel.LOW
                for risk in risks
            ),
            critical_risks=sum(
                risk.risk_level == RiskLevel.CRITICAL
                for risk in risks
            ),
            high_risks=sum(
                risk.risk_level == RiskLevel.HIGH
                for risk in risks
            ),
            medium_risks=sum(
                risk.risk_level == RiskLevel.MEDIUM
                for risk in risks
            ),
            low_risks=sum(
                risk.risk_level == RiskLevel.LOW
                for risk in risks
            ),
            top_risks=risks[: self.MAX_TOP_RISKS],
        )

    def _collect_suppliers(
        self,
        analysis: ProductionRiskAnalysisSchema,
    ) -> dict[UUID, _SupplierRiskData]:

        suppliers: dict[UUID, _SupplierRiskData] = {}

        for product in analysis.products:

            for material in product.risk_materials:

                if material.days_of_stock is None:
                    continue

                material_risk = self._get_material_risk(
                    material.days_of_stock,
                    material.suppliers,
                )

                for supplier in material.suppliers:

                    supplier_data = suppliers.get(
                        supplier.supplier_id,
                    )

                    if supplier_data is None:
                        supplier_data = _SupplierRiskData(
                            supplier_id=supplier.supplier_id,
                            supplier_name=supplier.supplier_name,
                            lead_time_days=supplier.lead_time_days,
                        )

                        suppliers[
                            supplier.supplier_id
                        ] = supplier_data

                    supplier_data.affected_materials.add(
                        material.material_id,
                    )

                    if material_risk == RiskLevel.CRITICAL:
                        supplier_data.critical_materials.add(
                            material.material_id,
                        )

                    elif material_risk == RiskLevel.HIGH:
                        supplier_data.high_risk_materials.add(
                            material.material_id,
                        )

        return suppliers

    def _get_material_risk(
        self,
        days_of_stock,
        suppliers,
    ) -> RiskLevel:

        if not suppliers:
            return RiskLevel.LOW

        minimum_lead_time = min(
            supplier.lead_time_days
            for supplier in suppliers
        )

        if days_of_stock < minimum_lead_time:
            return RiskLevel.CRITICAL

        if (
            days_of_stock
            <= minimum_lead_time * 1.25
        ):
            return RiskLevel.HIGH

        return RiskLevel.LOW

    def _build_supplier_risk(
        self,
        supplier: _SupplierRiskData,
    ) -> SupplierRiskOverviewItem:

        affected_materials = len(
            supplier.affected_materials,
        )

        critical_materials = len(
            supplier.critical_materials,
        )

        high_risk_materials = len(
            supplier.high_risk_materials,
        )

        risk_level = self._calculate_supplier_risk(
            critical_materials=critical_materials,
            high_risk_materials=high_risk_materials,
            affected_materials=affected_materials,
        )

        return SupplierRiskOverviewItem(
            supplier_id=supplier.supplier_id,
            supplier_name=supplier.supplier_name,
            lead_time_days=supplier.lead_time_days,
            affected_materials=affected_materials,
            critical_materials=critical_materials,
            high_risk_materials=high_risk_materials,
            risk_level=risk_level,
        )

    def _calculate_supplier_risk(
        self,
        *,
        critical_materials: int,
        high_risk_materials: int,
        affected_materials: int,
    ) -> RiskLevel:

        if critical_materials > 0:
            return RiskLevel.CRITICAL

        if high_risk_materials > 0:
            return RiskLevel.HIGH

        if affected_materials >= 2:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _risk_sort_key(
        self,
        risk: SupplierRiskOverviewItem,
    ) -> tuple:

        risk_priority = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3,
        }

        return (
            risk_priority[risk.risk_level],
            -risk.critical_materials,
            -risk.high_risk_materials,
            -risk.affected_materials,
        )