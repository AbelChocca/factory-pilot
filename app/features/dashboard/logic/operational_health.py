from app.features.dashboard.schema import (
    OperationalHealth,
)
from app.features.dashboard.repositories.operational_health import (
    OperationalHealthRepository,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
)
from app.features.dashboard.types import OperationalStatus


class OperationalHealthLogic:

    def __init__(
        self,
        repository: OperationalHealthRepository,
    ):
        self.repository = repository

    async def get(
        self,
        production_analysis: ProductionRiskAnalysisSchema,
    ) -> OperationalHealth:

        (
            low_stock_materials,
            out_of_stock_materials,
        ) = await self.repository.get_inventory_status_counts()

        pending_purchase_plans = (
            await self.repository.count_pending_purchase_plans()
        )

        total_materials = (
            await self.repository.count_materials()
        )

        high_risk_products = (
            production_analysis.high_risk_products
        )

        medium_risk_products = (
            production_analysis.medium_risk_products
        )

        products_analyzed = (
            production_analysis.products_analyzed
        )

        issues_requiring_attention = (
            self._calculate_issues_requiring_attention(
                low_stock_materials=low_stock_materials,
                out_of_stock_materials=out_of_stock_materials,
                high_risk_products=high_risk_products,
                medium_risk_products=medium_risk_products,
                pending_purchase_plans=pending_purchase_plans,
            )
        )

        score = self._calculate_score(
            total_materials=total_materials,
            low_stock_materials=low_stock_materials,
            out_of_stock_materials=out_of_stock_materials,
            products_analyzed=products_analyzed,
            high_risk_products=high_risk_products,
            medium_risk_products=medium_risk_products,
            pending_purchase_plans=pending_purchase_plans,
        )

        status = self._calculate_status(score)

        return OperationalHealth(
            score=score,
            status=status,
            issues_requiring_attention=(
                issues_requiring_attention
            ),
            low_stock_materials=low_stock_materials,
            out_of_stock_materials=out_of_stock_materials,
            high_risk_products=high_risk_products,
            medium_risk_products=medium_risk_products,
            pending_purchase_plans=pending_purchase_plans,
        )

    def _calculate_issues_requiring_attention(
        self,
        low_stock_materials: int,
        out_of_stock_materials: int,
        high_risk_products: int,
        medium_risk_products: int,
        pending_purchase_plans: int,
    ) -> int:

        return (
            low_stock_materials
            + out_of_stock_materials
            + high_risk_products
            + medium_risk_products
            + pending_purchase_plans
        )

    def _calculate_score(
        self,
        *,
        total_materials: int,
        low_stock_materials: int,
        out_of_stock_materials: int,
        products_analyzed: int,
        high_risk_products: int,
        medium_risk_products: int,
        pending_purchase_plans: int,
    ) -> int:

        if total_materials == 0:
            inventory_score = 100
        else:
            inventory_penalty = (
                (low_stock_materials * 0.5)
                + (out_of_stock_materials * 1.0)
            ) / total_materials

            inventory_score = max(
                0,
                100 - (inventory_penalty * 100),
            )

        if products_analyzed == 0:
            production_score = 100
        else:
            production_penalty = (
                (medium_risk_products * 0.5)
                + (high_risk_products * 1.0)
            ) / products_analyzed

            production_score = max(
                0,
                100 - (production_penalty * 100),
            )

        procurement_score = max(
            0,
            100 - (pending_purchase_plans * 10),
        )

        score = (
            inventory_score * 0.30
            + production_score * 0.50
            + procurement_score * 0.20
        )

        return round(score)

    def _calculate_status(
        self,
        score: int,
    ) -> OperationalStatus:

        if score >= 80:
            return OperationalStatus.HEALTHY

        if score >= 50:
            return OperationalStatus.ATTENTION

        return OperationalStatus.CRITICAL