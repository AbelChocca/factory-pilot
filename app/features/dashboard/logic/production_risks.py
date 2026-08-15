from app.features.dashboard.schema import (
    ProductionRiskOverviewItem,
    ProductionRiskSummary,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
)
from app.features.production_risk.production_risk_types import ProductionRiskLevel


class ProductionRisksLogic:

    async def get(
        self,
        production_analysis: ProductionRiskAnalysisSchema,
    ) -> ProductionRiskSummary:

        top_risks = self._get_top_risks(
            production_analysis,
        )

        return ProductionRiskSummary(
            products_analyzed=(
                production_analysis.products_analyzed
            ),
            low_risk_products=(
                production_analysis.low_risk_products
            ),
            medium_risk_products=(
                production_analysis.medium_risk_products
            ),
            high_risk_products=(
                production_analysis.high_risk_products
            ),
            critical_risk_products=(
                production_analysis.critical_risk_products
            ),
            top_risks=top_risks,
        )

    def _get_top_risks(
        self,
        analysis: ProductionRiskAnalysisSchema,
    ) -> list[ProductionRiskOverviewItem]:

        risk_order = {
            ProductionRiskLevel.CRITICAL: 0,
            ProductionRiskLevel.HIGH: 1,
            ProductionRiskLevel.MEDIUM: 2,
            ProductionRiskLevel.LOW: 3,
        }

        products = sorted(
            analysis.products,
            key=lambda product: (
                risk_order[product.risk_level],
                product.current_producible_units,
            ),
        )

        return [
            ProductionRiskOverviewItem(
                product_id=product.product_id,
                product_name=product.product_name,
                product_sku=product.product_sku,
                current_producible_units=(
                    product.current_producible_units
                ),
                risk_level=product.risk_level,
                bottleneck_material_name=(
                    product.bottleneck_material.material_name
                    if product.bottleneck_material
                    else None
                ),
            )
            for product in products[:5]
        ]