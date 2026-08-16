from typing import Any
from uuid import UUID

from app.ai.tools.ai_tool import AITool
from app.ai.chat.schemas.event_schemas import InventoryTrendAnalysisEvent
from app.features.inventory.schema import (
    InventoryTrendAnalysisContext,
)
from app.features.inventory.services.inventory_service import (
    InventoryService,
)
from app.features.inventory.types import InventoryOwnerType
from app.ai.chat.types import AIAgentStatus


class AnalyzeInventoryTrendsTool(AITool):

    def __init__(
        self,
        inventory_service: InventoryService,
    ):
        self.inventory_service = inventory_service

    @property
    def name(self) -> str:
        return "analyze_inventory_trends"

    @property
    def description(self) -> str:
        return (
            "Analyze inventory stock trends over a configurable period. "
            "Returns current stock, minimum stock, inflow and outflow, "
            "average daily consumption, coverage days, historical stock "
            "evolution, and whether each inventory item is increasing, "
            "decreasing, or stable."
        )

    @property
    def agent_status(self) -> AIAgentStatus:
        return AIAgentStatus.ANALYZING

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period_days": {
                    "anyOf": [
                        {
                            "type": "integer",
                            "minimum": 7,
                            "maximum": 365,
                        },
                        {
                            "type": "null",
                        },
                    ],
                    "description": (
                        "Number of previous days to analyze. "
                        "Use 30 when no specific period is requested."
                    ),
                },
                "owner_type": {
                    "anyOf": [
                        {
                            "type": "string",
                            "enum": [
                                owner_type.value
                                for owner_type in InventoryOwnerType
                            ],
                        },
                        {
                            "type": "null",
                        },
                    ],
                    "description": (
                        "Optional inventory owner type to analyze."
                    ),
                },
                "owner_id": {
                    "anyOf": [
                        {
                            "type": "string",
                        },
                        {
                            "type": "null",
                        },
                    ],
                    "description": (
                        "Optional UUID of a specific inventory owner."
                    ),
                },
            },
            "required": [
                "period_days",
                "owner_type",
                "owner_id",
            ],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> InventoryTrendAnalysisContext:

        arguments = arguments or {}

        period_days = arguments.get(
            "period_days",
            30,
        )

        owner_type = arguments.get("owner_type")

        if owner_type is not None:
            owner_type = InventoryOwnerType(owner_type)

        owner_id = arguments.get("owner_id")

        if owner_id is not None:
            owner_id = UUID(owner_id)

        return await self.inventory_service.analyze_inventory_trends(
            period_days=period_days,
            owner_type=owner_type,
            owner_id=owner_id,
        )

    def to_event(
        self,
        result: InventoryTrendAnalysisContext,
    ) -> InventoryTrendAnalysisEvent:

        return InventoryTrendAnalysisEvent(
            period_days=result.period_days,
            analyzed_from=result.analyzed_from,
            analyzed_to=result.analyzed_to,
            items=result.items,
            total_items=result.total_items,
            decreasing_items=result.decreasing_items,
            increasing_items=result.increasing_items,
            stable_items=result.stable_items,
        )