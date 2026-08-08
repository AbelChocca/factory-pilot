from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Numeric, Text, DateTime, String, func, Enum
from sqlmodel import Field, SQLModel

from app.features.inventory.types import InventoryMovementType
from app.shared.types import UnitType


class InventoryMovementTable(SQLModel, table=True):
    __tablename__ = "inventory_movements"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    inventory_id: UUID = Field(
        sa_column=Column(
            ForeignKey("inventory.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    movement_type: InventoryMovementType = Field(
        nullable=False,
    )

    previous_quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )

    quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )

    new_quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )

    owner_name: str = Field(
        sa_column=Column(
            String(150),
            nullable=False,
        )
    )

    owner_code: str = Field(
        sa_column=Column(
            String(50),
            nullable=False,
        )
    )

    unit_type: UnitType = Field(
        sa_column=Column(
            Enum(UnitType, name="unit_type"),
            nullable=False,
        )
    )

    reason: str | None = Field(
        default=None,
        sa_column=Column(
            Text,
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