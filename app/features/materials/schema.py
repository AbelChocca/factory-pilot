from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.enums import Status
from app.features.inventory.types import AvailabilityStatus
from app.features.materials.types import MaterialType
from app.shared.types import UnitType


class MaterialFilterSchema(BaseModel):
    query: str | None = None

    unit_type: UnitType | None = None

    availability_status: AvailabilityStatus | None = None

class CreateMaterialSchema(BaseModel):
    name: str = Field(max_length=150)

    description: str | None = None

    material_type: MaterialType

    unit_type: UnitType

    initial_stock: Decimal = Field(gt=0)

    initial_minimum_stock: Decimal = Field(gt=0)


class MaterialResponseSchema(BaseModel):
    id: UUID

    sku: str

    name: str

    description: str | None

    unit: str

    stock: Decimal

    minimum_stock: Decimal

    status: Status

    availability_status: AvailabilityStatus

    model_config = ConfigDict(
        from_attributes=True
    )