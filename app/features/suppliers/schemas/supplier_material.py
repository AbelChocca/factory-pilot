from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from app.shared.types import UnitType
from app.features.materials.types import MaterialType

class ReplaceMaterialSupplierItemSchema(BaseModel):
    supplier_id: UUID
    supplier_sku: str | None = None
    unit_price: Decimal | None = None
    preferred: bool = False

class MaterialSupplierDetailResponse(BaseModel):
    material_id: UUID
    supplier_id: UUID

    material_name: str
    material_sku: str
    unit_type: UnitType

    supplier_name: str
    supplier_sku: str | None

    unit_price: Decimal | None
    lead_time_days: int
    preferred: bool

class MaterialSupplierResponse(BaseModel):
    supplier_id: UUID
    supplier_name: str
    supplier_email: str | None
    supplier_phone: str | None
    lead_time_days: int

    supplier_sku: str | None
    unit_price: Decimal | None
    preferred: bool

class SupplierMaterialResponse(BaseModel):
    material_id: UUID
    material_name: str
    material_sku: str
    material_type: MaterialType
    unit_type: UnitType

    supplier_sku: str | None
    unit_price: Decimal | None
    preferred: bool