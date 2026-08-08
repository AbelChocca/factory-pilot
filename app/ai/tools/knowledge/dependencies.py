from fastapi import Depends

from app.ai.knowledge.knowledge_service import KnowledgeDocumentService
from app.ai.rag.context_builder import ContextBuilder, get_context_builder
from app.ai.tools.knowledge.search_knowledge import SearchKnowledgeTool
from app.ai.knowledge.dependencies import get_knowledge_document_service


def get_search_knowledge_tool(
    knowledge_service: KnowledgeDocumentService = Depends(
        get_knowledge_document_service,
    ),
    context_builder: ContextBuilder = Depends(
        get_context_builder
    )
) -> SearchKnowledgeTool:

    return SearchKnowledgeTool(
        knowledge_service=knowledge_service,
        context_builder=context_builder,
    )