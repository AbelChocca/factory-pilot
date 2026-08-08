from decimal import Decimal
from typing import Any
from uuid import UUID

from app.ai.tools.ai_tool import AITool
from app.features.purchase_plans.schema import (
    CreatePurchasePlanSchema,
    PurchasePlanItemCreateSchema,
    PurchasePlanResponse
)
from app.features.purchase_plans.service import PurchasePlanService

from app.ai.chat.schemas.event_schemas import PurchasePlanEvent


class GeneratePurchasePlanTool(AITool):

    def __init__(
        self,
        purchase_plan_service: PurchasePlanService,
    ):
        self.purchase_plan_service = purchase_plan_service

    @property
    def name(self) -> str:
        return "generate_purchase_plan"

    @property
    def description(self) -> str:
        return (
            "Generate a draft purchase plan for materials that need to be "
            "replenished. Before calling this tool, make sure the user has "
            "provided enough information to determine the purchase quantity "
            "for each material. The user may specify a target stock level "
            "(for example, 'bring MDF to 200 units') or an additional "
            "quantity to purchase (for example, 'buy 50 extra units of MDF'). "
            "If the user has not specified how much stock should be purchased, "
            "ask the user for the desired replenishment quantity or target "
            "stock level before calling this tool. "
            "Do not call this tool until the purchase quantity is determined. "
            "The tool validates supplier-material relationships and calculates "
            "unit prices, lead times, estimated costs, and total cost."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": (
                        "Materials to purchase, including the selected "
                        "supplier and purchase quantity."
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
                                    "Quantity of material to purchase."
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
            "required": ["items"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> Any:

        if not arguments or not arguments.get("items"):
            raise ValueError(
                "At least one purchase plan item is required."
            )

        items = []

        for item in arguments["items"]:
            quantity = Decimal(
                str(item["quantity"])
            )

            if quantity <= Decimal("0"):
                raise ValueError(
                    "Purchase quantity must be greater than zero."
                )

            items.append(
                PurchasePlanItemCreateSchema(
                    material_id=UUID(
                        item["material_id"]
                    ),
                    supplier_id=UUID(
                        item["supplier_id"]
                    ),
                    quantity=quantity,
                )
            )

        schema = CreatePurchasePlanSchema(
            items=items,
        )

        purcharse_plan = await self.purchase_plan_service.create(
            schema,
        )

        purcharse_plan_items = await self.purchase_plan_service.get_items(
            purcharse_plan.id
        )

        return PurchasePlanResponse(
            purchase_plan_id=purcharse_plan.id,
            total_estimated_cost=purcharse_plan.total_estimated_cost,
            items=purcharse_plan_items
        )

    def to_event(
        self,
        result: PurchasePlanResponse,
    ) -> PurchasePlanEvent:

        return PurchasePlanEvent(
            purchase_plan_id=result.purchase_plan_id,
            items=result.items,
            total_estimated_cost=float(
                result.total_estimated_cost
            ),
        )