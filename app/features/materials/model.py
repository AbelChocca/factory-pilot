from uuid import UUID, uuid4

from sqlalchemy import Column, Enum, String, Text
from sqlmodel import Field, SQLModel

from app.shared.enums import Status
from app.shared.types import UnitType
from app.features.materials.types import MaterialType


class MaterialTable(SQLModel, table=True):
    __tablename__ = "materials"

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

    material_type: MaterialType = Field(
        sa_column=Column(
            Enum(MaterialType, name="material_type"),
            nullable=False,
        )
    )

    unit_type: UnitType = Field(
        sa_column=Column(
            Enum(UnitType, name="unit_type"),
            nullable=False,
        )
    )

    status: Status = Field(
        default=Status.ACTIVE,
        sa_column=Column(
            Enum(Status, name="status"),
            nullable=False,
        )
    )