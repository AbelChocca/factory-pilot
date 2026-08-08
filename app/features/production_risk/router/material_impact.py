from uuid import UUID

from fastapi import APIRouter, Depends

from app.features.production_risk.analyzer.material_impact import (
    MaterialImpactAnalyzer,
)
from app.features.production_risk.dependencies.analyzers import (
    get_material_impact_analyzer,
)
from app.features.production_risk.production_risk_schema import (
    MaterialImpactContext,
)


material_impact_router = APIRouter(
    prefix="/material-impact",
    tags=["Material Impact"],
)


@material_impact_router.get(
    "/analyze/{material_id}",
    response_model=MaterialImpactContext,
)
async def analyze_material_impact(
    material_id: UUID,
    analyzer: MaterialImpactAnalyzer = Depends(
        get_material_impact_analyzer,
    ),
) -> MaterialImpactContext:

    return await analyzer.analyze(
        material_id=material_id,
    )