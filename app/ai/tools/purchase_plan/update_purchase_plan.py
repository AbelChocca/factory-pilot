from decimal import Decimal
from typing import Any
from uuid import UUID

from app.ai.chat.schemas.event_schemas import AIEvent, PurchasePlanUpdatedEvent
from app.ai.tools.ai_tool import AITool
from app.features.purchase_plans.schema import (
    UpdatePurchasePlanSchema,
    PurchasePlanResponse
)
from app.features.purchase_plans.service import PurchasePlanService


class UpdatePurchasePlanTool(AITool):

    def __init__(
        self,
        purchase_plan_service: PurchasePlanService,
    ):
        self.purchase_plan_service = purchase_plan_service

    @property
    def name(self) -> str:
        return "update_purchase_plan"

    @property
    def description(self) -> str:
        return (
            "Update an existing draft purchase plan by replacing its "
            "current items with the complete set of items specified "
            "by the user. Use this tool when the user wants to add, "
            "remove, or modify materials or quantities in a purchase "
            "plan. The provided items represent the final desired "
            "state of the purchase plan. If a current item is not "
            "included, it will be removed. If a new material is "
            "included, it will be added. The supplier and quantity "
            "must be specified for every item."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "purchase_plan_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": (
                        "ID of the draft purchase plan to update."
                    ),
                },
                "items": {
                    "type": "array",
                    "description": (
                        "Complete final list of materials that should "
                        "remain in the purchase plan. Items not included "
                        "in this list will be removed."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "material_id": {
                                "type": "string",
                                "format": "uuid",
                                "description": (
                                    "ID of the material to purchase."
                                ),
                            },
                            "supplier_id": {
                                "type": "string",
                                "format": "uuid",
                                "description": (
                                    "ID of the supplier to purchase "
                                    "the material from."
                                ),
                            },
                            "quantity": {
                                "type": "number",
                                "description": (
                                    "Final quantity to purchase."
                                ),
                            },
                        },
                        "required": [
                            "material_id",
                            "supplier_id",
                            "quantity",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": [
                "purchase_plan_id",
                "items",
            ],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> PurchasePlanResponse:

        if not arguments:
            raise ValueError(
                "Purchase plan update arguments are required."
            )

        schema = UpdatePurchasePlanSchema(
            purchase_plan_id=UUID(
                arguments["purchase_plan_id"],
            ),
            items=[
                {
                    "material_id": UUID(
                        item["material_id"],
                    ),
                    "supplier_id": UUID(
                        item["supplier_id"],
                    ),
                    "quantity": Decimal(
                        str(item["quantity"]),
                    ),
                }
                for item in arguments["items"]
            ],
        )

        purchase_plan = await self.purchase_plan_service.update(
            schema,
        )

        purchase_plan_items = await self.purchase_plan_service.get_items(
            purchase_plan_id=purchase_plan.id
        )

        return PurchasePlanResponse(
            purchase_plan_id=purchase_plan.id,
            items=purchase_plan_items,
            total_estimated_cost=purchase_plan.total_estimated_cost
        )

    def to_event(
        self,
        result: PurchasePlanResponse,
    ) -> AIEvent:

        return PurchasePlanUpdatedEvent(
            purchase_plan_id=result.purchase_plan_id,
            items=result.items,
            total_estimated_cost=float(result.total_estimated_cost)
        )