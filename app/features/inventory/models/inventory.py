from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric, UniqueConstraint, func
from sqlmodel import Field, SQLModel

from app.features.inventory.types import InventoryOwnerType

class InventoryTable(SQLModel, table=True):
    __tablename__ = "inventory"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    owner_type: InventoryOwnerType = Field(
        nullable=False,
    )

    owner_id: UUID = Field(
        nullable=False,
    )

    quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )

    minimum_quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )

    last_movement_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
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

    __table_args__ = (
        UniqueConstraint(
            "owner_type",
            "owner_id",
            name="uq_inventory_owner",
        ),
    )