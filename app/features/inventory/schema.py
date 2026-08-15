from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.inventory.types import InventoryMovementType, InventoryOwnerType, InventoryTrend
from app.shared.types import UnitType


class InventoryMovementFilterSchema(BaseModel):
    query: str | None = None

    movement_type: InventoryMovementType | None = None

    owner_type: InventoryOwnerType | None = None

    owner_id: UUID | None = None

    created_from: datetime | None = None

    created_to: datetime | None = None

class InventoryMovementResponseSchema(BaseModel):
    id: UUID

    inventory_id: UUID

    movement_type: InventoryMovementType

    previous_quantity: Decimal

    quantity: Decimal

    new_quantity: Decimal

    owner_name: str

    owner_code: str

    unit_type: UnitType

    reason: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

class CreateInventoryMovementSchema(BaseModel):
    movement_type: InventoryMovementType

    owner_type: InventoryOwnerType

    owner_id: UUID

    reason: str | None = Field(None)

    quantity: Decimal = Field(gt=0)

class LowStockMaterial(BaseModel):
    material_id: UUID
    sku: str
    name: str
    quantity: Decimal
    minimum_quantity: Decimal
    unit_type: str

class InventoryTrendPoint(BaseModel):
    date: datetime
    quantity: Decimal

class InventoryTrendItem(BaseModel):
    owner_id: UUID
    owner_type: InventoryOwnerType

    owner_name: str
    owner_code: str
    unit_type: UnitType

    current_quantity: Decimal
    minimum_quantity: Decimal

    average_daily_outflow: Decimal
    average_daily_inflow: Decimal

    coverage_days: Decimal | None

    trend: InventoryTrend

    total_inflow: Decimal
    total_outflow: Decimal

    history: list[InventoryTrendPoint]

class InventoryTrendAnalysisContext(BaseModel):
    period_days: int
    analyzed_from: datetime
    analyzed_to: datetime
    items: list[InventoryTrendItem]

    total_items: int
    decreasing_items: int
    increasing_items: int
    stable_items: int

class InventoryOwnerInfo(BaseModel):
    owner_name: str
    owner_code: str
    unit_type: UnitType