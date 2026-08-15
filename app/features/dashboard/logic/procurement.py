from decimal import Decimal
from uuid import UUID

from app.features.dashboard.repositories.procurement import (
    ProcurementItemRow,
    ProcurementRepository,
)
from app.features.dashboard.schema import (
    ProcurementAction,
    ProcurementSummary,
)
from app.features.dashboard.types import (
    ProcurementPriority,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
    ProductionRiskMaterialSchema
)
from app.features.purchase_plans.types import (
    PurchasePlanStatus,
)


class ProcurementLogic:

    MAX_TOP_ACTIONS = 5

    def __init__(
        self,
        repository: ProcurementRepository,
    ):
        self.repository = repository

    async def get(
        self,
        production_analysis: ProductionRiskAnalysisSchema,
    ) -> ProcurementSummary:

        draft_purchase_plans = (
            await self.repository.count_by_status(
                PurchasePlanStatus.DRAFT,
            )
        )

        approved_purchase_plans = (
            await self.repository.count_by_status(
                PurchasePlanStatus.APPROVED,
            )
        )

        pending_cost = (
            await self.repository.get_pending_cost()
        )

        pending_items = (
            await self.repository.get_pending_items()
        )

        material_risks = self._build_material_risk_map(
            production_analysis,
        )

        actions = [
            self._build_action(
                item=item,
                material_risk=material_risks.get(
                    item.material_id,
                ),
            )
            for item in pending_items
        ]

        actions.sort(
            key=self._action_sort_key,
        )

        critical_materials = len({
            action.material_id
            for action in actions
            if action.priority
            == ProcurementPriority.CRITICAL
        })

        return ProcurementSummary(
            draft_purchase_plans=draft_purchase_plans,
            approved_purchase_plans=approved_purchase_plans,
            pending_purchase_plans=(
                draft_purchase_plans
                + approved_purchase_plans
            ),
            materials_to_replenish=len({
                action.material_id
                for action in actions
            }),
            estimated_pending_cost=pending_cost,
            critical_materials=critical_materials,
            top_actions=actions[
                : self.MAX_TOP_ACTIONS
            ],
        )

    def _build_material_risk_map(
        self,
        analysis: ProductionRiskAnalysisSchema,
    ) -> dict[UUID, ProductionRiskMaterialSchema]:

        material_risks = {}

        for product in analysis.products:

            for material in product.risk_materials:

                material_risks.setdefault(
                    material.material_id,
                    material,
                )

        return material_risks

    def _build_action(
        self,
        *,
        item: ProcurementItemRow,
        material_risk: ProductionRiskMaterialSchema | None,
    ) -> ProcurementAction:

        priority = self._calculate_priority(
            material_risk=material_risk,
            lead_time_days=item.lead_time_days,
        )

        return ProcurementAction(
            purchase_plan_id=item.purchase_plan_id,
            status=item.purchase_plan_status,

            material_id=item.material_id,
            material_name=item.material_name,

            supplier_id=item.supplier_id,
            supplier_name=item.supplier_name,

            quantity=item.quantity,
            estimated_cost=item.estimated_cost,

            lead_time_days=item.lead_time_days,

            priority=priority,
        )

    def _calculate_priority(
        self,
        *,
        material_risk: ProductionRiskMaterialSchema | None,
        lead_time_days: int,
    ) -> ProcurementPriority:

        if material_risk is None:
            return ProcurementPriority.NORMAL

        days_of_stock = material_risk.days_of_stock

        if days_of_stock is None:
            return ProcurementPriority.NORMAL

        if days_of_stock <= Decimal(lead_time_days):
            return ProcurementPriority.CRITICAL

        if days_of_stock <= (
            Decimal(lead_time_days) + Decimal("3")
        ):
            return ProcurementPriority.HIGH

        return ProcurementPriority.NORMAL

    def _action_sort_key(
        self,
        action: ProcurementAction,
    ) -> tuple:

        priority_order = {
            ProcurementPriority.CRITICAL: 0,
            ProcurementPriority.HIGH: 1,
            ProcurementPriority.NORMAL: 2,
        }

        return (
            priority_order[action.priority],
            -action.estimated_cost,
        )