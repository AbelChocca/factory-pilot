from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from uuid import UUID

from app.features.inventory.types import AvailabilityStatus
from app.shared.enums import Status


class ProductFilterSchema(BaseModel):
    query: str | None = None
    availability_status: AvailabilityStatus | None = None

class CreateProductSchema(BaseModel):
    name: str = Field(max_length=150)

    description: str | None = None

    initial_stock: Decimal = Field(ge=0)

    initial_minimum_stock: Decimal = Field(ge=0)

class ProductResponseSchema(BaseModel):
    id: UUID

    sku: str

    name: str

    description: str | None

    stock: Decimal

    minimum_stock: Decimal

    status: Status

    availability_status: AvailabilityStatus

    model_config = ConfigDict(
        from_attributes=True
    )