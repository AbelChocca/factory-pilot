from typing import Any

from app.ai.knowledge.knowledge_service import KnowledgeDocumentService
from app.ai.rag.context_builder import ContextBuilder
from app.ai.tools.ai_tool import AITool


class SearchKnowledgeTool(AITool):

    def __init__(
        self,
        knowledge_service: KnowledgeDocumentService,
        context_builder: ContextBuilder
    ):
        self.knowledge_service = knowledge_service
        self.context_builder = context_builder

    @property
    def name(self) -> str:
        return "search_knowledge"

    @property
    def description(self) -> str:
        return (
            "Search the NorthWood Manufacturing knowledge base "
            "for relevant information about products, materials, "
            "production, suppliers, and company operations."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The information to search for in the "
                        "NorthWood Manufacturing knowledge base."
                    ),
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        arguments: dict[str, Any] | None = None,
    ) -> str:

        if not arguments:
            raise ValueError("Search query is required.")

        query = arguments["query"]

        documents = await self.knowledge_service.search(
            query=query,
            limit=5,
            similarity_threshold=0.55,
        )

        return self.context_builder.build(documents)