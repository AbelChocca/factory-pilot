from typing import Any

from app.ai.tools.ai_tool import AITool
from app.features.production_risk.analyzer.production_risk import (
    ProductionRiskAnalyzer,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskLLMContextSchema,
)
from app.ai.chat.schemas.event_schemas import ProductionRiskAnalysisEvent


class AnalyzeProductionRiskTool(AITool):

    def __init__(
        self,
        analyzer: ProductionRiskAnalyzer,
    ):
        self.analyzer = analyzer

    @property
    def name(self) -> str:
        return "analyze_production_risk"

    @property
    def description(self) -> str:
        return (
            "Analyze current production risks across products "
            "using material inventory, consumption, production "
            "capacity, and supplier lead time data. Use this tool "
            "when the user asks about production risks, products "
            "at risk, production bottlenecks, or which materials "
            "may disrupt production."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> ProductionRiskLLMContextSchema:

        analysis = await self.analyzer.execute()

        return self.analyzer.to_llm_context(
            analysis,
        )

    def to_event(
        self,
        result: ProductionRiskLLMContextSchema,
    ) -> ProductionRiskAnalysisEvent:

        return ProductionRiskAnalysisEvent(
            analysis_period_days=result.analysis_period_days,
            products_analyzed=result.products_analyzed,
            high_risk_products=result.high_risk_products,
            medium_risk_products=result.medium_risk_products,
            low_risk_products=result.low_risk_products,
            products=result.products,
        )