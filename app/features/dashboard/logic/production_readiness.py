from app.features.dashboard.repositories.production_readiness import (
    ProductionReadinessRepository,
)
from app.features.dashboard.schema import (
    ProductionReadiness,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
)


class ProductionReadinessLogic:

    def __init__(
        self,
        repository: ProductionReadinessRepository,
    ):
        self.repository = repository

    async def get(
        self,
        production_analysis: ProductionRiskAnalysisSchema,
    ) -> ProductionReadiness:

        total_products = (
            await self.repository.count_products()
        )

        low_risk_products = (
            production_analysis.low_risk_products
        )

        medium_risk_products = (
            production_analysis.medium_risk_products
        )

        high_risk_products = (
            production_analysis.high_risk_products
        )

        critical_risk_products = (
            production_analysis.critical_risk_products
        )

        readiness_percentage = (
            self._calculate_readiness_percentage(
                total_products=total_products,
                low_risk_products=low_risk_products,
                medium_risk_products=medium_risk_products,
                high_risk_products=high_risk_products,
                critical_risk_products=critical_risk_products,
            )
        )

        return ProductionReadiness(
            total_products=total_products,
            low_risk_products=low_risk_products,
            medium_risk_products=medium_risk_products,
            high_risk_products=high_risk_products,
            critical_risk_products=critical_risk_products,
            readiness_percentage=readiness_percentage,
        )

    def _calculate_readiness_percentage(
        self,
        *,
        total_products: int,
        low_risk_products: int,
        medium_risk_products: int,
        high_risk_products: int,
        critical_risk_products: int,
    ) -> int:

        if total_products == 0:
            return 100

        weighted_readiness = (
            low_risk_products * 1.0
            + medium_risk_products * 0.7
            + high_risk_products * 0.3
            + critical_risk_products * 0.0
        )

        return round(
            weighted_readiness
            / total_products
            * 100
        )