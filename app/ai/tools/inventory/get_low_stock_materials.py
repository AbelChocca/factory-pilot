from typing import Any

from app.ai.tools.ai_tool import AITool
from app.features.inventory.schema import LowStockMaterial
from app.features.inventory.services.inventory_service import InventoryService

from app.ai.chat.schemas.event_schemas import LowStockMaterialEvent

class GetLowStockMaterialsTool(AITool):

    def __init__(
        self,
        inventory_service: InventoryService,
    ):
        self.inventory_service = inventory_service

    @property
    def name(self) -> str:
        return "get_low_stock_materials"

    @property
    def description(self) -> str:
        return (
            "Get all materials whose current stock is below "
            "their minimum stock level."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> list[LowStockMaterial]:

        return await self.inventory_service.get_low_stock_materials()

    def to_event(
        self,
        result: list[LowStockMaterial],
    ) -> LowStockMaterialEvent:

        return LowStockMaterialEvent(
            materials=result,
        )