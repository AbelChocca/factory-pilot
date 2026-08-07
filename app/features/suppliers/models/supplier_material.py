from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlmodel import Field, SQLModel


class SupplierMaterialTable(SQLModel, table=True):
    __tablename__ = "supplier_materials"

    __table_args__ = (
        PrimaryKeyConstraint(
            "supplier_id",
            "material_id",
            name="pk_supplier_material",
        ),
    )

    supplier_id: UUID = Field(
        sa_column=Column(
            ForeignKey("suppliers.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    material_id: UUID = Field(
        sa_column=Column(
            ForeignKey("materials.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    supplier_sku: str | None = Field(
        default=None,
        max_length=50,
    )

    unit_price: Decimal | None = Field(
        default=None,
        sa_column=Column(
            Numeric(12, 2),
            nullable=True,
        ),
    )

    preferred: bool = Field(
        nullable=False,
        default=False,
    )