from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class KnowledgeDocumentTable(SQLModel, table=True):
    __tablename__ = "knowledge_documents"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    content: str = Field(
        sa_column=Column(
            Text,
            nullable=False,
        )
    )

    source: str = Field(
        index=True,
        nullable=False,
    )

    document_type: str = Field(
        nullable=False,
    )

    document_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column(
            JSONB,
            nullable=False,
        ),
    )

    embedding: list[float] = Field(
        sa_column=Column(
            VECTOR(768),
            nullable=False,
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )