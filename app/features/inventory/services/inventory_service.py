from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.features.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.features.inventory.schema import (
    InventoryTrendAnalysisContext,
    InventoryTrendItem,
    InventoryTrendPoint,
    LowStockMaterial,
)
from app.features.inventory.types import (
    InventoryMovementType,
    InventoryOwnerType,
    InventoryTrend,
)


class InventoryService:

    def __init__(
        self,
        inventory_repository: InventoryRepository,
    ):
        self.inventory_repository = inventory_repository

    async def get_low_stock_materials(
        self,
    ) -> list[LowStockMaterial]:

        rows = await self.inventory_repository.get_low_stock_materials()

        return [
            LowStockMaterial(
                material_id=material.id,
                sku=material.sku,
                name=material.name,
                quantity=inventory.quantity,
                minimum_quantity=inventory.minimum_quantity,
                unit_type=material.unit_type.value,
            )
            for inventory, material in rows
        ]

    async def analyze_inventory_trends(
        self,
        period_days: int = 30,
        owner_type: InventoryOwnerType | None = None,
        owner_id=None,
    ) -> InventoryTrendAnalysisContext:

        analyzed_to = datetime.now(timezone.utc)

        analyzed_from = (
            analyzed_to - timedelta(days=period_days)
        )

        inventory_rows = (
            await self.inventory_repository.get_for_trend_analysis(
                owner_type=owner_type,
                owner_id=owner_id,
            )
        )

        inventories = [
            inventory
            for inventory, _ in inventory_rows
        ]

        inventory_ids = [
            inventory.id
            for inventory in inventories
        ]

        movements = (
            await self.inventory_repository
            .get_movements_for_trend_analysis(
                inventory_ids=inventory_ids,
                created_from=analyzed_from,
                created_to=analyzed_to,
            )
        )

        movements_by_inventory = {}

        for movement in movements:
            movements_by_inventory.setdefault(
                movement.inventory_id,
                [],
            ).append(movement)

        items: list[InventoryTrendItem] = []

        for inventory, owner_info in inventory_rows:

            inventory_movements = movements_by_inventory.get(
                inventory.id,
                [],
            )

            total_inflow = Decimal("0")
            total_outflow = Decimal("0")

            history: list[InventoryTrendPoint] = []

            for movement in inventory_movements:

                if self._is_inflow(movement.movement_type):
                    total_inflow += movement.quantity

                elif self._is_outflow(movement.movement_type):
                    total_outflow += movement.quantity

                history.append(
                    InventoryTrendPoint(
                        date=movement.created_at,
                        quantity=movement.new_quantity,
                    )
                )

            average_daily_inflow = (
                total_inflow / Decimal(period_days)
            )

            average_daily_outflow = (
                total_outflow / Decimal(period_days)
            )

            coverage_days = None

            if average_daily_outflow > 0:
                coverage_days = (
                    inventory.quantity
                    / average_daily_outflow
                )

            trend = self._calculate_trend(
                inventory_movements=inventory_movements,
            )

            items.append(
                InventoryTrendItem(
                    owner_id=inventory.owner_id,
                    owner_type=inventory.owner_type,
                    owner_name=owner_info.owner_name,
                    owner_code=owner_info.owner_code,
                    unit_type=owner_info.unit_type,
                    current_quantity=inventory.quantity,
                    minimum_quantity=inventory.minimum_quantity,
                    average_daily_outflow=average_daily_outflow,
                    average_daily_inflow=average_daily_inflow,
                    coverage_days=coverage_days,
                    trend=trend,
                    total_inflow=total_inflow,
                    total_outflow=total_outflow,
                    history=history,
                )
            )

        return InventoryTrendAnalysisContext(
            period_days=period_days,
            analyzed_from=analyzed_from,
            analyzed_to=analyzed_to,
            items=items,
            total_items=len(items),
            decreasing_items=sum(
                1
                for item in items
                if item.trend == InventoryTrend.DECREASING
            ),
            increasing_items=sum(
                1
                for item in items
                if item.trend == InventoryTrend.INCREASING
            ),
            stable_items=sum(
                1
                for item in items
                if item.trend == InventoryTrend.STABLE
            ),
        )

    @staticmethod
    def _calculate_trend(
        inventory_movements,
    ) -> InventoryTrend:

        if not inventory_movements:
            return InventoryTrend.STABLE

        first_quantity = (
            inventory_movements[0].previous_quantity
        )

        last_quantity = (
            inventory_movements[-1].new_quantity
        )

        if first_quantity == 0:
            if last_quantity > 0:
                return InventoryTrend.INCREASING

            return InventoryTrend.STABLE

        variation = (
            last_quantity - first_quantity
        ) / first_quantity

        if variation > Decimal("0.05"):
            return InventoryTrend.INCREASING

        if variation < Decimal("-0.05"):
            return InventoryTrend.DECREASING

        return InventoryTrend.STABLE

    @staticmethod
    def _is_inflow(
        movement_type: InventoryMovementType,
    ) -> bool:
        return movement_type in {
            InventoryMovementType.IN,
        }

    @staticmethod
    def _is_outflow(
        movement_type: InventoryMovementType,
    ) -> bool:
        return movement_type in {
            InventoryMovementType.OUT,
        }