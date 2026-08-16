from typing import Any
from uuid import UUID

from app.ai.tools.ai_tool import AITool
from app.features.suppliers.schemas.supplier_material import (
    MaterialSupplierDetailResponse
)
from app.features.suppliers.services.supplier_material import (
    SupplierMaterialService,
)

from app.ai.chat.schemas.event_schemas import SupplierRecommendationEvent
from app.ai.chat.types import AIAgentStatus


class GetMaterialSuppliersTool(AITool):

    def __init__(
        self,
        supplier_material_service: SupplierMaterialService,
    ):
        self.supplier_material_service = supplier_material_service

    @property
    def name(self) -> str:
        return "get_material_suppliers"

    @property
    def description(self) -> str:
        return (
            "Get all suppliers associated with the specified materials. "
            "Returns supplier information including supplier name, "
            "supplier SKU, unit price, and whether the supplier is preferred."
        )

    @property
    def agent_status(self) -> AIAgentStatus:
        return AIAgentStatus.THINKING

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "material_ids": {
                    "type": "array",
                    "description": (
                        "List of material IDs to retrieve suppliers for."
                    ),
                    "items": {
                        "type": "string",
                        "format": "uuid",
                    },
                },
            },
            "required": ["material_ids"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> list[MaterialSupplierDetailResponse]:

        if not arguments or not arguments.get("material_ids"):
            raise ValueError(
                "At least one material_id is required."
            )

        material_ids = list(
            dict.fromkeys(
                UUID(material_id)
                for material_id in arguments["material_ids"]
            )
        )

        return await self.supplier_material_service.get_material_suppliers(
            material_ids
        )

    def to_event(
        self,
        result: list[MaterialSupplierDetailResponse],
    ) -> SupplierRecommendationEvent:

        return SupplierRecommendationEvent(
            materials=result,
        )