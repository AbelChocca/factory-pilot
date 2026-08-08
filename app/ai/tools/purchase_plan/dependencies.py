from fastapi import Depends

from app.ai.tools.purchase_plan.approve_purchase_plan import (
    ApprovePurchasePlanTool,
)
from app.ai.tools.purchase_plan.generate_purchase_plan import (
    GeneratePurchasePlanTool,
)
from app.ai.tools.purchase_plan.update_purchase_plan import (
    UpdatePurchasePlanTool,
)
from app.features.purchase_plans.dependencies.service import (
    get_purchase_plan_service,
)
from app.features.purchase_plans.service import (
    PurchasePlanService,
)


def get_generate_purchase_plan_tool(
    purchase_plan_service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
) -> GeneratePurchasePlanTool:
    return GeneratePurchasePlanTool(
        purchase_plan_service=purchase_plan_service,
    )


def get_update_purchase_plan_tool(
    purchase_plan_service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
) -> UpdatePurchasePlanTool:
    return UpdatePurchasePlanTool(
        purchase_plan_service=purchase_plan_service,
    )


def get_approve_purchase_plan_tool(
    purchase_plan_service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
) -> ApprovePurchasePlanTool:
    return ApprovePurchasePlanTool(
        purchase_plan_service=purchase_plan_service,
    )