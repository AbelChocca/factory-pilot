from decimal import Decimal
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Numeric, PrimaryKeyConstraint
from sqlmodel import Field, SQLModel


class ProductMaterialTable(SQLModel, table=True):
    __tablename__ = "product_materials"

    __table_args__ = (
        PrimaryKeyConstraint(
            "product_id",
            "material_id",
            name="pk_product_material",
        ),
    )

    product_id: UUID = Field(
        sa_column=Column(
            ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    material_id: UUID = Field(
        sa_column=Column(
            ForeignKey("materials.id", ondelete="RESTRICT"),
            nullable=False,
        )
    )

    quantity: Decimal = Field(
        sa_column=Column(
            Numeric(12, 2),
            nullable=False,
        )
    )