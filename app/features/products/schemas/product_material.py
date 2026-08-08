from uuid import UUID

from pydantic import BaseModel, Field
from decimal import Decimal

from app.shared.types import UnitType
from app.features.materials.types import MaterialType


class ProductMaterialResponse(BaseModel):
    material_id: UUID
    material_name: str
    material_sku: str
    material_type: MaterialType
    unit_type: UnitType
    quantity: Decimal

class MaterialProductResponse(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str
    quantity: Decimal

class ReplaceProductMaterialItemSchema(BaseModel):
    material_id: UUID
    quantity: Decimal = Field(
        gt=0,
        decimal_places=2,
    )