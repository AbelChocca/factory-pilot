from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.knowledge.knowledge_model import (
    KnowledgeDocumentTable,
)


class KnowledgeDocumentRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def save(
        self,
        document: KnowledgeDocumentTable,
    ) -> KnowledgeDocumentTable:

        self.session.add(document)

        await self.session.commit()
        await self.session.refresh(document)

        return document

    async def save_many(
        self,
        documents: list[KnowledgeDocumentTable],
    ) -> list[KnowledgeDocumentTable]:

        self.session.add_all(documents)

        await self.session.commit()

    async def get_by_id(
        self,
        document_id: UUID,
    ) -> KnowledgeDocumentTable | None:

        statement = (
            select(KnowledgeDocumentTable)
            .where(
                KnowledgeDocumentTable.id == document_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_source(
        self,
        source: str,
    ) -> list[KnowledgeDocumentTable]:

        statement = (
            select(KnowledgeDocumentTable)
            .where(
                KnowledgeDocumentTable.source == source
            )
            .order_by(
                KnowledgeDocumentTable.created_at.asc()
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def delete(
        self,
        document_id: UUID,
    ) -> bool:

        statement = delete(
            KnowledgeDocumentTable
        ).where(
            KnowledgeDocumentTable.id == document_id
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    async def delete_by_source(
        self,
        source: str,
    ) -> int:

        statement = delete(
            KnowledgeDocumentTable
        ).where(
            KnowledgeDocumentTable.source == source
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount

    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        similarity_threshold: float = 0.75,
    ) -> list[tuple[KnowledgeDocumentTable, float]]:

        distance = (
            KnowledgeDocumentTable.embedding.cosine_distance(
                embedding
            )
        )

        distance_threshold = 1 - similarity_threshold

        similarity = 1 - distance

        statement = (
            select(
                KnowledgeDocumentTable,
                similarity.label("similarity"),
                )
            .where(
                distance <= distance_threshold
            )
            .order_by(distance)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.all())