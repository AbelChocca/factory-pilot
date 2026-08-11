from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from decimal import Decimal
from app.shared.types import UnitType
from app.features.purchase_plans.types import PurchasePlanStatus

class UpdatePurchasePlanItemSchema(BaseModel):
    material_id: UUID
    supplier_id: UUID
    quantity: Decimal = Field(gt=0)


class UpdatePurchasePlanSchema(BaseModel):
    items: list[UpdatePurchasePlanItemSchema]

class PurchasePlanResponseSchema(BaseModel):
    id: UUID
    status: PurchasePlanStatus
    total_estimated_cost: Decimal
    created_at: datetime
    updated_at: datetime

class PurchasePlanItemCreateSchema(BaseModel):
    material_id: UUID
    supplier_id: UUID

    quantity: Decimal = Field(
        gt=0,
    )

class PurchasePlanItem(BaseModel):
    material_id: UUID
    material_name: str

    supplier_id: UUID
    supplier_name: str

    quantity: Decimal
    unit_type: UnitType

    unit_price: Decimal
    estimated_cost: Decimal

    lead_time_days: int
    preferred_supplier: bool

class PurchasePlanResponse(BaseModel):
    purchase_plan_id: UUID
    total_estimated_cost: Decimal

    items: list[PurchasePlanItem]

class CreatePurchasePlanSchema(BaseModel):
    items: list[PurchasePlanItemCreateSchema] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_unique_items(self):
        combinations = [
            (
                item.material_id,
                item.supplier_id,
            )
            for item in self.items
        ]

        if len(combinations) != len(set(combinations)):
            raise ValueError(
                "Each material and supplier combination "
                "must be unique."
            )

        return self