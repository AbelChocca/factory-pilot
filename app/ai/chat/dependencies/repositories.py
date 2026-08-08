from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chat.repositories.conversation_repository import (
    AIConversationRepository,
)
from app.db.dependencies import get_db_session


def get_ai_conversation_repository(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> AIConversationRepository:

    return AIConversationRepository(
        session=session,
    )