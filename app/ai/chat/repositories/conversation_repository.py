from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chat.models.conversation_model import AIConversationTable


class AIConversationRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_id(
        self,
        conversation_id: UUID,
    ) -> AIConversationTable | None:

        result = await self.session.execute(
            select(AIConversationTable).where(
                AIConversationTable.id == conversation_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
    ) -> AIConversationTable:

        conversation = AIConversationTable()

        self.session.add(conversation)

        await self.session.commit()

        await self.session.refresh(
            conversation,
        )

        return conversation

    async def update_response_id(
        self,
        conversation: AIConversationTable,
        response_id: str,
    ) -> AIConversationTable:

        conversation.previous_response_id = response_id
        conversation.updated_at = datetime.now(
            timezone.utc
        )

        self.session.add(conversation)

        await self.session.commit()

        await self.session.refresh(
            conversation,
        )

        return conversation