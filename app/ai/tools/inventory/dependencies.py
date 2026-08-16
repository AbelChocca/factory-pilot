from fastapi import Depends

from app.ai.tools.inventory.get_low_stock_materials import (
    GetLowStockMaterialsTool,
)
from app.ai.tools.inventory.analyze_inventory_trends import (
    AnalyzeInventoryTrendsTool,
)
from app.features.inventory.services.inventory_service import InventoryService
from app.features.inventory.dependencies.service import get_inventory_service


def get_low_stock_materials_tool(
    inventory_service: InventoryService = Depends(
        get_inventory_service,
    ),
) -> GetLowStockMaterialsTool:
    return GetLowStockMaterialsTool(
        inventory_service=inventory_service,
    )

def get_analyze_inventory_trends_tool(
    inventory_service: InventoryService = Depends(
        get_inventory_service,
    ),
) -> AnalyzeInventoryTrendsTool:

    return AnalyzeInventoryTrendsTool(
        inventory_service=inventory_service,
    )