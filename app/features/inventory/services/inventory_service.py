from app.features.inventory.repositories.inventory_repository import (
    InventoryRepository,
)

from app.features.inventory.schema import LowStockMaterial

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