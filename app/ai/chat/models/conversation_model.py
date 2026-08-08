from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Column, DateTime


class AIConversationTable(SQLModel, table=True):
    __tablename__ = "ai_conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    previous_response_id: str | None = Field(
        default=None,
        nullable=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        ),
    )