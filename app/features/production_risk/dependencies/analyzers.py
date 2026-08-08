
from app.features.production_risk.dependencies.repositories import get_production_risk_repository
from app.features.production_risk.repository import ProductionAnalysisRepository
from app.features.production_risk.analyzer.production_risk import (
    ProductionRiskAnalyzer,
)
from app.features.production_risk.analyzer.material_impact import (
    MaterialImpactAnalyzer,
)

from fastapi import Depends


def get_production_risk_analyzer(
    repository: ProductionAnalysisRepository = Depends(
        get_production_risk_repository,
    ),
) -> ProductionRiskAnalyzer:

    return ProductionRiskAnalyzer(
        repository=repository,
    )

def get_material_impact_analyzer(
    repository: ProductionAnalysisRepository = Depends(
        get_production_risk_repository,
    ),
) -> MaterialImpactAnalyzer:

    return MaterialImpactAnalyzer(
        repository=repository,
    )