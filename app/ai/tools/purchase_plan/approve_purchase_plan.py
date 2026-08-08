from typing import Any
from uuid import UUID
from app.ai.chat.schemas.event_schemas import AIEvent, PurchasePlanApprovedEvent
from app.features.purchase_plans.schema import (
    PurchasePlanResponse
)
from app.ai.tools.ai_tool import AITool
from app.features.purchase_plans.model import PurchasePlanTable
from app.features.purchase_plans.service import PurchasePlanService


class ApprovePurchasePlanTool(AITool):

    def __init__(
        self,
        purchase_plan_service: PurchasePlanService,
    ):
        self.purchase_plan_service = purchase_plan_service

    @property
    def name(self) -> str:
        return "approve_purchase_plan"

    @property
    def description(self) -> str:
        return (
            "Approve an existing draft purchase plan. "
            "Use this tool only when the user explicitly confirms "
            "that the purchase plan should be approved. "
            "Approval makes the purchase plan no longer editable."
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
                        "ID of the draft purchase plan to approve."
                    ),
                },
            },
            "required": [
                "purchase_plan_id",
            ],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> PurchasePlanTable:

        if not arguments:
            raise ValueError(
                "Purchase plan ID is required."
            )

        purchase_plan_id = UUID(
            arguments["purchase_plan_id"],
        )

        purchase_plan = (
            await self.purchase_plan_service.approve(
                purchase_plan_id,
            )
        )

        if purchase_plan is None:
            raise ValueError(
                "Purchase plan not found."
            )

        purchase_plan_items = await self.purchase_plan_service.get_items(purchase_plan.id)

        return PurchasePlanResponse(
            purchase_plan_id=purchase_plan.id,
            items=purchase_plan_items,
            total_estimated_cost=purchase_plan.total_estimated_cost
        )

    def to_event(
        self,
        result: PurchasePlanResponse,
    ) -> AIEvent:
        return PurchasePlanApprovedEvent(
            purchase_plan_id=result.purchase_plan_id,
            items=result.items,
            total_estimated_cost=float(
                result.total_estimated_cost,
            ),
        )