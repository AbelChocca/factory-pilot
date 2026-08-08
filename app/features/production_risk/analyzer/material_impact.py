from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.features.production_risk.repository import (
    ProductionAnalysisRepository,
)
from app.features.production_risk.production_risk_schema import (
    MaterialImpactContext,
)
from app.features.production_risk.production_risk_types import MaterialImpactLevel


class MaterialImpactAnalyzer:

    def __init__(
        self,
        repository: ProductionAnalysisRepository,
    ):
        self.repository = repository

    async def analyze(
        self,
        material_id: UUID,
        period_days: int = 30,
    ) -> MaterialImpactContext:

        material = await self.repository.get_material_by_id(material_id)

        if not material_id:
            raise ValueError(
                "Material not found."
            )

        since = datetime.now(timezone.utc) - timedelta(days=period_days)

        product_materials = (
            await self.repository.get_product_materials(
                material_ids=[material_id],
            )
        )

        inventories = (
            await self.repository.get_material_inventory(
                material_ids=[material_id],
            )
        )

        movements = (
            await self.repository.get_material_movement_summary(
                material_ids=[material_id],
                since=since,
            )
        )

        suppliers = (
            await self.repository.get_material_suppliers(
                material_ids=[material_id],
            )
        )

        inventory = next(
            (
                item
                for item in inventories
                if item.material_id == material_id
            ),
            None,
        )

        if inventory is None:
            raise ValueError(
                f"Inventory not found for material {material_id}"
            )

        movement = next(
            (
                item
                for item in movements
                if item.material_id == material_id
            ),
            None,
        )

        total_outbound = (
            movement.total_outbound
            if movement
            else Decimal("0")
        )

        outbound_movements = (
            movement.outbound_movements
            if movement
            else 0
        )

        daily_consumption = (
            total_outbound / Decimal(period_days)
            if total_outbound > 0
            else Decimal("0")
        )

        stock_coverage_days = (
            inventory.quantity / daily_consumption
            if daily_consumption > 0
            else None
        )

        supplier_lead_times = [
            supplier.lead_time_days
            for supplier in suppliers
            if supplier.lead_time_days is not None
        ]

        min_lead_time_days = (
            min(supplier_lead_times)
            if supplier_lead_times
            else None
        )

        affected_products_count = len(
            {
                item.product_id
                for item in product_materials
            }
        )

        impact_level = self._calculate_impact_level(
            current_quantity=inventory.quantity,
            minimum_quantity=inventory.minimum_quantity,
            stock_coverage_days=stock_coverage_days,
            min_lead_time_days=min_lead_time_days,
            affected_products_count=affected_products_count,
            supplier_count=len(suppliers),
        )

        return MaterialImpactContext(
            material_id=material_id,
            material_name=material.name,
            material_sku=material.sku,
            impact_level=impact_level,
            current_quantity=inventory.quantity,
            minimum_quantity=inventory.minimum_quantity,
            total_outbound=total_outbound,
            outbound_movements=outbound_movements,
            stock_coverage_days=stock_coverage_days,
            min_lead_time_days=min_lead_time_days,
            affected_products_count=affected_products_count,
            supplier_count=len(suppliers),
        )

    def _calculate_impact_level(
        self,
        current_quantity: Decimal,
        minimum_quantity: Decimal,
        stock_coverage_days: Decimal | None,
        min_lead_time_days: int | None,
        affected_products_count: int,
        supplier_count: int,
    ) -> MaterialImpactLevel:

        score = 0

        if current_quantity <= minimum_quantity:
            score += 2

        if (
            stock_coverage_days is not None
            and min_lead_time_days is not None
            and stock_coverage_days < min_lead_time_days
        ):
            score += 3

        if affected_products_count >= 5:
            score += 2
        elif affected_products_count >= 3:
            score += 1

        if supplier_count == 0:
            score += 3
        elif supplier_count == 1:
            score += 2

        if score >= 5:
            return MaterialImpactLevel.HIGH

        if score >= 2:
            return MaterialImpactLevel.MEDIUM

        return MaterialImpactLevel.LOW