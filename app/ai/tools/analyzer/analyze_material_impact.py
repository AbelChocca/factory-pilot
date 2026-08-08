from typing import Any
from uuid import UUID

from app.ai.chat.schemas.event_schemas import MaterialImpactAnalysisEvent
from app.ai.tools.ai_tool import AITool
from app.features.production_risk.analyzer.material_impact import (
    MaterialImpactAnalyzer,
)
from app.features.production_risk.production_risk_schema import (
    MaterialImpactContext,
)


class AnalyzeMaterialImpactTool(AITool):

    def __init__(
        self,
        analyzer: MaterialImpactAnalyzer,
    ):
        self.analyzer = analyzer

    @property
    def name(self) -> str:
        return "analyze_material_impact"

    @property
    def description(self) -> str:
        return (
            "Analyze the production impact of a specific material "
            "using its current inventory, minimum stock level, "
            "consumption, product dependencies, and supplier "
            "lead time data. Use this tool when the user asks "
            "about the impact, criticality, or production risk "
            "of a specific material."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "material_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": (
                        "UUID of the material to analyze."
                    ),
                },
            },
            "required": ["material_id"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> MaterialImpactContext:

        if not arguments or "material_id" not in arguments:
            raise ValueError(
                "material_id is required"
            )

        material_id = UUID(
            arguments["material_id"]
        )

        return await self.analyzer.analyze(
            material_id=material_id,
        )

    def to_event(
        self,
        result: MaterialImpactContext,
    ) -> MaterialImpactAnalysisEvent:

        return MaterialImpactAnalysisEvent(
            material_id=result.material_id,
            material_name=result.material_name,
            material_sku=result.material_sku,
            impact_level=result.impact_level,
            current_quantity=result.current_quantity,
            minimum_quantity=result.minimum_quantity,
            total_outbound=result.total_outbound,
            outbound_movements=result.outbound_movements,
            stock_coverage_days=result.stock_coverage_days,
            min_lead_time_days=result.min_lead_time_days,
            affected_products_count=result.affected_products_count,
            supplier_count=result.supplier_count,
        )