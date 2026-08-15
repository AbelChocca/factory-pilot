from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.features.dashboard.repositories.material_coverage import (
    MaterialCoverageRepository,
    MaterialInventoryRow,
    MaterialMovementSummaryRow,
)
from app.features.dashboard.schema import (
    MaterialCoverageRisk,
    MaterialCoverageSummary,
)
from app.features.dashboard.types import (
    MaterialCoverageStatus,
)


class MaterialCoverageLogic:

    ANALYSIS_PERIOD_DAYS = 30

    CRITICAL_DAYS = Decimal("3")
    LOW_COVERAGE_DAYS = Decimal("7")

    MAX_TOP_RISKS = 5

    def __init__(
        self,
        repository: MaterialCoverageRepository,
    ):
        self.repository = repository

    async def execute(
        self,
    ) -> MaterialCoverageSummary:

        inventory = (
            await self.repository.get_material_inventory()
        )

        if not inventory:
            return MaterialCoverageSummary(
                materials_tracked=0,
                critical_materials=0,
                low_coverage_materials=0,
                average_days_of_stock=None,
                minimum_days_of_stock=None,
                top_risks=[],
            )

        since = (
            datetime.now(timezone.utc)
            - timedelta(
                days=self.ANALYSIS_PERIOD_DAYS,
            )
        )

        movements = (
            await self.repository.get_material_movement_summary(
                since,
            )
        )

        movements_by_material = {
            row.material_id: row
            for row in movements
        }

        risks = []

        for material in inventory:

            movement = movements_by_material.get(
                material.material_id,
            )

            risk = self._build_material_coverage(
                material=material,
                movement=movement,
            )

            risks.append(risk)

        critical_materials = sum(
            risk.status
            == MaterialCoverageStatus.CRITICAL
            for risk in risks
        )

        low_coverage_materials = sum(
            risk.status
            == MaterialCoverageStatus.LOW
            for risk in risks
        )

        days_with_coverage = [
            risk.days_of_stock
            for risk in risks
            if risk.days_of_stock is not None
        ]

        average_days = (
            sum(days_with_coverage)
            / Decimal(len(days_with_coverage))
            if days_with_coverage
            else None
        )

        minimum_days = (
            min(days_with_coverage)
            if days_with_coverage
            else None
        )

        risks.sort(
            key=self._risk_sort_key,
        )

        return MaterialCoverageSummary(
            materials_tracked=len(risks),
            critical_materials=critical_materials,
            low_coverage_materials=low_coverage_materials,
            average_days_of_stock=average_days,
            minimum_days_of_stock=minimum_days,
            top_risks=risks[
                : self.MAX_TOP_RISKS
            ],
        )

    def _build_material_coverage(
        self,
        *,
        material: MaterialInventoryRow,
        movement: MaterialMovementSummaryRow | None,
    ) -> MaterialCoverageRisk:

        total_outbound = (
            movement.total_outbound
            if movement
            else Decimal("0")
        )

        average_daily_consumption = (
            total_outbound
            / Decimal(str(self.ANALYSIS_PERIOD_DAYS))
        )

        days_of_stock = (
            material.current_stock
            / average_daily_consumption
            if average_daily_consumption > 0
            else None
        )

        status = self._calculate_status(
            days_of_stock,
        )

        return MaterialCoverageRisk(
            material_id=material.material_id,
            material_name=material.material_name,
            material_sku=material.material_sku,
            current_stock=material.current_stock,
            average_daily_consumption=(
                average_daily_consumption
            ),
            days_of_stock=days_of_stock,
            status=status,
        )

    def _calculate_status(
        self,
        days_of_stock: Decimal | None,
    ) -> MaterialCoverageStatus:

        if days_of_stock is None:
            return MaterialCoverageStatus.NO_CONSUMPTION

        if days_of_stock <= self.CRITICAL_DAYS:
            return MaterialCoverageStatus.CRITICAL

        if days_of_stock <= self.LOW_COVERAGE_DAYS:
            return MaterialCoverageStatus.LOW

        return MaterialCoverageStatus.HEALTHY

    def _risk_sort_key(
        self,
        risk: MaterialCoverageRisk,
    ) -> tuple:

        status_order = {
            MaterialCoverageStatus.CRITICAL: 0,
            MaterialCoverageStatus.LOW: 1,
            MaterialCoverageStatus.HEALTHY: 2,
            MaterialCoverageStatus.NO_CONSUMPTION: 3,
        }

        days = (
            risk.days_of_stock
            if risk.days_of_stock is not None
            else Decimal("999999")
        )

        return (
            status_order[risk.status],
            days,
        )