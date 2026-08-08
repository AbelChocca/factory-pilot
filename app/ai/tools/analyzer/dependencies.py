from fastapi import Depends

from app.ai.tools.analyzer.analyze_production_risk import (
    AnalyzeProductionRiskTool,
)
from app.features.production_risk.dependencies.analyzers import (
    get_production_risk_analyzer,
)
from app.features.production_risk.analyzer.production_risk import (
    ProductionRiskAnalyzer,
)
from app.ai.tools.analyzer.analyze_material_impact import (
    AnalyzeMaterialImpactTool,
)
from app.features.production_risk.analyzer.material_impact import (
    MaterialImpactAnalyzer,
)
from app.features.production_risk.dependencies.analyzers import (
    get_material_impact_analyzer,
)

def get_analyze_production_risk_tool(
    analyzer: ProductionRiskAnalyzer = Depends(
        get_production_risk_analyzer,
    ),
) -> AnalyzeProductionRiskTool:

    return AnalyzeProductionRiskTool(
        analyzer=analyzer,
    )


def get_analyze_material_impact_tool(
    analyzer: MaterialImpactAnalyzer = Depends(
        get_material_impact_analyzer,
    ),
) -> AnalyzeMaterialImpactTool:

    return AnalyzeMaterialImpactTool(
        analyzer=analyzer,
    )