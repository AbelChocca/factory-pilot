from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.features.purchase_plans.types import PurchasePlanStatus


class PurchasePlanTable(SQLModel, table=True):
    __tablename__ = "purchase_plans"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    status: PurchasePlanStatus = Field(
        default=PurchasePlanStatus.DRAFT,
        index=True,
    )

    total_estimated_cost: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        ),
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

    items: list["PurchasePlanItemTable"] = Relationship(
        back_populates="purchase_plan",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
        },
    )


class PurchasePlanItemTable(SQLModel, table=True):
    __tablename__ = "purchase_plan_items"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
    )

    purchase_plan_id: UUID = Field(
        foreign_key="purchase_plans.id",
        nullable=False,
        index=True,
    )

    material_id: UUID = Field(
        foreign_key="materials.id",
        nullable=False,
        index=True,
    )

    supplier_id: UUID = Field(
        foreign_key="suppliers.id",
        nullable=False,
        index=True,
    )

    quantity: Decimal = Field(
        sa_column=Column(
            Numeric(10, 2),
            nullable=False,
        ),
    )

    unit_price: Decimal = Field(
        sa_column=Column(
            Numeric(10, 2),
            nullable=False,
        ),
    )

    estimated_cost: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        ),
    )

    lead_time_days: int = Field(
        nullable=False,
    )

    preferred_supplier: bool = Field(
        default=False,
        nullable=False,
    )

    purchase_plan: PurchasePlanTable = Relationship(
        back_populates="items",
    )