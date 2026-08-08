from fastapi import APIRouter, Depends

from app.features.production_risk.dependencies.analyzers import (
    get_production_risk_analyzer,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
)
from app.features.production_risk.analyzer.production_risk import (
    ProductionRiskAnalyzer,
)

production_risk_router = APIRouter(
    prefix="/production-risk",
    tags=["Production Risk"],
)


@production_risk_router.get(
    "/analyze",
    response_model=ProductionRiskAnalysisSchema,
)
async def analyze_production_risk(
    analyzer: ProductionRiskAnalyzer = Depends(
        get_production_risk_analyzer,
    ),
) -> ProductionRiskAnalysisSchema:

    return await analyzer.execute()