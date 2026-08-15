from decimal import Decimal

from app.features.inventory.types import InventoryOwnerType

from app.features.dashboard.schema import (
    InventoryHealth,
    InventoryHealthSection,
)

from app.features.inventory.types import (
    InventoryHealthStatus,
)
from app.features.dashboard.repositories.inventory_health import InventoryHealthRepository, InventoryHealthCounts


class InventoryHealthLogic:

    LOW_STOCK_WEIGHT = Decimal("0.5")

    HEALTHY_THRESHOLD = 80
    ATTENTION_THRESHOLD = 60

    def __init__(
        self,
        repository: InventoryHealthRepository,
    ):
        self.repository = repository

    async def get(self) -> InventoryHealth:

        material_counts = (
            await self.repository.get_health_counts(
                InventoryOwnerType.MATERIAL,
            )
        )

        product_counts = (
            await self.repository.get_health_counts(
                InventoryOwnerType.PRODUCT,
            )
        )

        materials = self._build_section(
            material_counts,
        )

        products = self._build_section(
            product_counts,
        )

        overall_percentage = self._calculate_overall_percentage(
            materials.health_percentage,
            products.health_percentage,
        )

        return InventoryHealth(
            materials=materials,
            products=products,
            overall_percentage=overall_percentage,
            overall_status=self._calculate_status(
                overall_percentage,
            ),
        )
    
    def _build_section(
        self,
        counts: InventoryHealthCounts,
    ) -> InventoryHealthSection:

        health_percentage = (
            self._calculate_health_percentage(
                counts,
            )
        )

        return InventoryHealthSection(
            total_items=counts.total,
            available_items=counts.available,
            low_stock_items=counts.low_stock,
            out_of_stock_items=counts.out_of_stock,
            health_percentage=health_percentage,
            status=self._calculate_status(
                health_percentage,
            ),
        )

    def _calculate_health_percentage(
        self,
        counts: InventoryHealthCounts,
    ) -> int:

        if counts.total == 0:
            return 100

        score = (
            Decimal(counts.available)
            + (
                Decimal(counts.low_stock)
                * self.LOW_STOCK_WEIGHT
            )
        )

        percentage = (
            score
            / Decimal(counts.total)
            * Decimal("100")
        )

        return round(percentage)

    def _calculate_status(
        self,
        percentage: int,
    ) -> InventoryHealthStatus:

        if percentage >= self.HEALTHY_THRESHOLD:
            return InventoryHealthStatus.HEALTHY

        if percentage >= self.ATTENTION_THRESHOLD:
            return InventoryHealthStatus.ATTENTION

        return InventoryHealthStatus.CRITICAL

    def _calculate_overall_percentage(
        self,
        material_percentage: int,
        product_percentage: int,
    ) -> int:

        return round(
            (
                material_percentage
                + product_percentage
            )
            / 2
        )