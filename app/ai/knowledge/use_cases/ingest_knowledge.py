import asyncio
from pathlib import Path

from app.ai.knowledge.markdown_chunker import MarkdownChunker
from app.ai.knowledge.markdown_loader import MarkdownLoader
from app.ai.knowledge.knowledge_model import KnowledgeDocumentTable
from app.ai.knowledge.knowledge_service import (
    KnowledgeDocumentService
)
from app.ai.knowledge.knowledge_repository import (
    KnowledgeDocumentRepository,
)
from app.ai.clients.openai_embedding_client import (
    OpenAIEmbeddingClient,
)
from app.db.dependencies import async_session_factory
from app.db.config import engine

class IngestKnowledgeUseCase:

    def __init__(
        self,
        loader: MarkdownLoader,
        chunker: MarkdownChunker,
        service: KnowledgeDocumentService,
    ):
        self.loader = loader
        self.chunker = chunker
        self.service = service

    async def execute(self) -> int:

        documents = self.loader.load()

        chunks = []

        for document in documents:
            await self.service.delete_by_source(
                document.source
            )
            
            chunks.extend(
                self.chunker.chunk(document)
            )

        if not chunks:
            return 0

        await self.service.index_documents(
            chunks
        )

        return len(chunks)

async def main():

    async with engine.begin() as conn:

        await conn.run_sync(
            KnowledgeDocumentTable.__table__.create,
            checkfirst=True,
        )

    async with async_session_factory() as session:

        repository = KnowledgeDocumentRepository(
            session=session,
        )

        embedding_client = OpenAIEmbeddingClient()

        service = KnowledgeDocumentService(
            repository=repository,
            embedding_client=embedding_client,
        )

        loader = MarkdownLoader(
            knowledge_path=Path("knowledge"),
        )

        chunker = MarkdownChunker()

        use_case = IngestKnowledgeUseCase(
            loader=loader,
            chunker=chunker,
            service=service,
        )

        count = await use_case.execute()

        print(
            f"Knowledge ingestion completed: "
            f"{count} chunks indexed."
        )


if __name__ == "__main__":
    asyncio.run(main())