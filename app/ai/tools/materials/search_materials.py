from typing import Any

from app.ai.tools.ai_tool import AITool
from app.features.materials.schema import MaterialFilterSchema
from app.features.materials.service import MaterialService
from app.features.materials.schema import (
    MaterialSearchResultSchema,
)


class SearchMaterialsTool(AITool):

    def __init__(
        self,
        material_service: MaterialService,
    ):
        self.material_service = material_service

    @property
    def name(self) -> str:
        return "search_materials"

    @property
    def description(self) -> str:
        return (
            "Search for materials by name, SKU, or description "
            "and return matching material candidates with their "
            "UUIDs, stock, minimum stock, unit, and availability. "
            "Use this tool when the user refers to a material by "
            "name or SKU but its UUID is not known. If multiple "
            "materials match, present the candidates to the user "
            "and ask which material they mean before calling "
            "another material-specific tool."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Material name, SKU, or description "
                        "to search for."
                    ),
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> list[MaterialSearchResultSchema]:

        if not arguments or "query" not in arguments:
            raise ValueError("query is required")

        query = arguments["query"].strip()

        if not query:
            raise ValueError("query cannot be empty")

        result = await self.material_service.get(
            filters=MaterialFilterSchema(
                query=query,
            ),
            page=1,
            limit=5,
        )

        return [
            MaterialSearchResultSchema(
                id=material.id,
                sku=material.sku,
                name=material.name,
                unit=material.unit,
            )
            for material in result.items
        ]