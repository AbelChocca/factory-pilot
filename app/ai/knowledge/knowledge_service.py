from app.ai.knowledge.knowledge_dto import KnowledgeDocument
from app.ai.clients.openai_embedding_client import (
    OpenAIEmbeddingClient,
)
from app.ai.knowledge.knowledge_model import (
    KnowledgeDocumentTable,
)
from app.ai.knowledge.knowledge_repository import (
    KnowledgeDocumentRepository,
)

from app.ai.knowledge.schema import RetrievedKnowledgeDocument


class KnowledgeDocumentService:

    def __init__(
        self,
        repository: KnowledgeDocumentRepository,
        embedding_client: OpenAIEmbeddingClient,
    ):
        self.repository = repository
        self.embedding_client = embedding_client

    async def index_documents(
        self,
        documents: list[KnowledgeDocument],
    ) -> list[KnowledgeDocumentTable]:

        if not documents:
            return []

        embeddings = await self.embedding_client.embed_many(
            [document.content for document in documents]
        )

        tables = [
            KnowledgeDocumentTable(
                content=document.content,
                source=document.source,
                document_type=document.document_type,
                document_metadata=document.metadata,
                embedding=embedding,
            )
            for document, embedding in zip(
                documents,
                embeddings,
                strict=True,
            )
        ]

        return await self.repository.save_many(tables)

    async def search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.75,
    ) -> list[RetrievedKnowledgeDocument]:

        embedding = await self.embedding_client.embed(query)

        documents = await self.repository.search_similar(
            embedding=embedding,
            limit=limit,
            similarity_threshold=similarity_threshold,
        )

        return [
                RetrievedKnowledgeDocument(
                    content=document.content,
                    source=document.source,
                    metadata=document.document_metadata,
                    similarity=similarity
                )
                for document, similarity in documents
            ]
            

    async def delete_by_source(
        self,
        source: str,
    ) -> int:

        return await self.repository.delete_by_source(source)