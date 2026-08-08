from pathlib import Path

from app.ai.clients.openai_embedding_client import (
    OpenAIEmbeddingClient,
    get_openai_embedding_client
)
from app.ai.knowledge.markdown_chunker import MarkdownChunker
from app.ai.knowledge.markdown_loader import MarkdownLoader
from app.ai.knowledge.knowledge_repository import (
    KnowledgeDocumentRepository
)
from app.ai.knowledge.knowledge_service import (
    KnowledgeDocumentService
)
from app.ai.knowledge.use_cases.ingest_knowledge import (
    IngestKnowledgeUseCase
)

from app.db.dependencies import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

def get_knowledge_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> KnowledgeDocumentRepository:

    return KnowledgeDocumentRepository(
        session=session,
    )

def get_knowledge_document_service(
    repository: KnowledgeDocumentRepository = Depends(
        get_knowledge_document_repository,
    ),
    embedding_client: OpenAIEmbeddingClient = Depends(
        get_openai_embedding_client,
    ),
) -> KnowledgeDocumentService:

    return KnowledgeDocumentService(
        repository=repository,
        embedding_client=embedding_client,
    )

def get_markdown_loader() -> MarkdownLoader:

    return MarkdownLoader(
        knowledge_path=Path("knowledge"),
    )

def get_markdown_chunker() -> MarkdownChunker:

    return MarkdownChunker()

def get_ingest_knowledge_use_case(
    loader: MarkdownLoader = Depends(
        get_markdown_loader,
    ),
    chunker: MarkdownChunker = Depends(
        get_markdown_chunker,
    ),
    service: KnowledgeDocumentService = Depends(
        get_knowledge_document_service,
    ),
) -> IngestKnowledgeUseCase:

    return IngestKnowledgeUseCase(
        loader=loader,
        chunker=chunker,
        service=service,
    )