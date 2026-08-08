from app.ai.knowledge.knowledge_service import KnowledgeDocumentService
from app.ai.rag.context_builder import ContextBuilder
from app.ai.clients.gemini_llm_client import GeminiLLMClient

from collections.abc import AsyncIterator

class RagUseCase:

    def __init__(
        self,
        knowledge_service: KnowledgeDocumentService,
        context_builder: ContextBuilder,
        llm_client: GeminiLLMClient,
    ):
        self.knowledge_service = knowledge_service
        self.context_builder = context_builder
        self.llm_client = llm_client

    async def execute(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.65,
    ) -> str:

        documents = await self.knowledge_service.search(query, limit, similarity_threshold)

        context = self.context_builder.build(documents)

        prompt = self._build_prompt(
            query=query,
            context=context,
        )

        return await self.llm_client.generate(prompt)

    async def execute_stream(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.65,
    ) -> AsyncIterator[str]:

        documents = await self.knowledge_service.search(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold,
        )

        context = self.context_builder.build(documents)

        prompt = self._build_prompt(
            query=query,
            context=context,
        )

        async for chunk in self.llm_client.generate_stream(prompt):
            yield chunk

    def _build_prompt(
        self,
        query: str,
        context: str,
    ) -> str:

        return f"""
You are an assistant for QH Factory Pilot.

Answer the user's question using only the provided context.

If the context does not contain enough information to answer the question,
say that you don't have enough information.

Context:
{context}

Question:
{query}

Answer:
""".strip()