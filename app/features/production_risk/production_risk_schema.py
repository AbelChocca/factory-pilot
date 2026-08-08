from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.shared.types import UnitType
from app.features.inventory.types import AvailabilityStatus
from app.features.production_risk.production_risk_types import ProductionRiskLevel, ConsumptionTrend, ProductionRiskFactorType, MaterialImpactLevel

# SCHEMA RESPONSE

class MaterialImpactContext(BaseModel):
    material_id: UUID
    material_name: str
    material_sku: str

    impact_level: MaterialImpactLevel

    current_quantity: Decimal
    minimum_quantity: Decimal

    total_outbound: Decimal
    outbound_movements: int

    stock_coverage_days: Decimal | None
    min_lead_time_days: int | None

    affected_products_count: int
    supplier_count: int

class ProductionRiskFactorSchema(BaseModel):
    owner_id: UUID
    owner_name: str
    factor: str
    severity: ProductionRiskLevel
    value: Decimal | None = None
    description: str

class ProductionRiskSupplierSchema(BaseModel):
    supplier_id: UUID
    supplier_name: str

    lead_time_days: int
    unit_price: Decimal

    preferred: bool


class ProductionRiskMaterialSchema(BaseModel):
    material_id: UUID
    material_name: str
    material_sku: str
    unit_type: UnitType

    current_stock: Decimal
    minimum_stock: Decimal

    required_per_product: Decimal
    producible_units: Decimal

    average_daily_consumption: Decimal
    days_of_stock: Decimal | None

    stock_status: AvailabilityStatus
    consumption_trend: ConsumptionTrend

    suppliers: list[ProductionRiskSupplierSchema]

class ProductionRiskProductSchema(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str

    current_producible_units: Decimal
    risk_level: ProductionRiskLevel

    risk_factors: list[ProductionRiskFactorSchema]

    bottleneck_material: ProductionRiskMaterialSchema | None
    risk_materials: list[ProductionRiskMaterialSchema]

class ProductionRiskAnalysisSchema(BaseModel):
    analysis_period_days: int

    products_analyzed: int

    high_risk_products: int
    medium_risk_products: int
    low_risk_products: int

    products: list[ProductionRiskProductSchema]

## LLM Context 

class ProductionRiskLLMFactorSchema(BaseModel):
    factor: ProductionRiskFactorType
    severity: ProductionRiskLevel
    owner_id: UUID
    owner_name: str
    value: Decimal | None
    description: str


class ProductionRiskLLMMaterialSchema(BaseModel):
    material_id: UUID
    material_name: str
    current_stock: Decimal
    minimum_stock: Decimal
    required_per_product: Decimal
    producible_units: Decimal
    average_daily_consumption: Decimal
    days_of_stock: Decimal | None


class ProductionRiskLLMProductSchema(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str

    risk_level: ProductionRiskLevel
    current_producible_units: Decimal

    bottleneck_material: ProductionRiskLLMMaterialSchema

    risk_factors: list[ProductionRiskLLMFactorSchema]


class ProductionRiskLLMContextSchema(BaseModel):
    analysis_period_days: int

    products_analyzed: int
    high_risk_products: int
    medium_risk_products: int
    low_risk_products: int

    products: list[ProductionRiskLLMProductSchema]

# Repository responses schema

class ProductMaterialAnalysisRow(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str

    material_id: UUID
    material_name: str
    material_sku: str
    material_unit_type: UnitType

    required_quantity: Decimal

class MaterialInventoryAnalysisRow(BaseModel):
    material_id: UUID
    quantity: Decimal
    minimum_quantity: Decimal

class MaterialMovementSummaryRow(BaseModel):
    material_id: UUID

    total_inbound: Decimal
    total_outbound: Decimal
    total_adjustments: Decimal

    outbound_movements: int

class MaterialSupplierAnalysisRow(BaseModel):
    material_id: UUID

    supplier_id: UUID
    supplier_name: str

    lead_time_days: int
    unit_price: Decimal | None
    preferred: bool

