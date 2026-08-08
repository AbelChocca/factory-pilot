from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum, String, Text, Column, DateTime, func
from sqlmodel import Field, SQLModel

from app.shared.enums import Status

class ProductTable(SQLModel, table=True):
    __tablename__ = "products"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    sku: str = Field(
        sa_column=Column(
            String(50),
            unique=True,
            nullable=False,
        )
    )

    name: str = Field(
        sa_column=Column(
            String(150),
            nullable=False,
        )
    )

    description: str | None = Field(
        default=None,
        sa_column=Column(
            Text,
            nullable=True,
        )
    )

    status: Status = Field(
        default=Status.ACTIVE,
        sa_column=Column(
            Enum(Status, name="status"),
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

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )