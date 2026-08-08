from app.ai.rag.rag_use_case import RagUseCase
from app.ai.knowledge.dependencies import get_knowledge_document_service
from app.ai.knowledge.knowledge_service import KnowledgeDocumentService
from app.ai.rag.context_builder import ContextBuilder, get_context_builder
from app.ai.clients.openai_llm_client import OpenAILLMClient, get_openai_llm_client

from fastapi import Depends

def get_rag_use_case(
    knowledge_service: KnowledgeDocumentService = Depends(get_knowledge_document_service),
    context_builder: ContextBuilder = Depends(get_context_builder),
    llm_client: OpenAILLMClient = Depends(get_openai_llm_client)
) -> RagUseCase:
    return RagUseCase(
        knowledge_service=knowledge_service,
        context_builder=context_builder,
        llm_client=llm_client
    )