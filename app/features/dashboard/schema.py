from decimal import Decimal

from pydantic import BaseModel, Field
from uuid import UUID
from app.features.production_risk.production_risk_types import ProductionRiskLevel
from app.features.inventory.types import InventoryHealthStatus
from app.features.purchase_plans.types import PurchasePlanStatus

from app.features.dashboard.types import (
    OperationalStatus,
    RiskLevel,
    ProcurementPriority,
    MaterialCoverageStatus
)

# ============================================================
# Operational Health
# ============================================================


class OperationalHealth(BaseModel):
    score: int = Field(ge=0, le=100)
    status: OperationalStatus

    issues_requiring_attention: int = Field(ge=0)

    low_stock_materials: int = Field(ge=0)
    out_of_stock_materials: int = Field(ge=0)

    high_risk_products: int = Field(ge=0)
    medium_risk_products: int = Field(ge=0)

    pending_purchase_plans: int = Field(ge=0)



# ============================================================
# Production Readiness
# ============================================================


class ProductionReadiness(BaseModel):
    total_products: int = Field(ge=0)

    low_risk_products: int
    medium_risk_products: int
    high_risk_products: int
    critical_risk_products: int

    readiness_percentage: int


# ============================================================
# Inventory Health
# ============================================================

class InventoryHealthSection(BaseModel):
    total_items: int = Field(ge=0)

    available_items: int = Field(ge=0)
    low_stock_items: int = Field(ge=0)
    out_of_stock_items: int = Field(ge=0)

    health_percentage: int = Field(ge=0, le=100)
    status: InventoryHealthStatus


class InventoryHealth(BaseModel):
    materials: InventoryHealthSection
    products: InventoryHealthSection

    overall_percentage: int = Field(
        ge=0,
        le=100,
    )

    overall_status: InventoryHealthStatus


# ============================================================
# Procurement / Purchase Plans
# ============================================================

class ProcurementAction(BaseModel):
    purchase_plan_id: UUID

    material_id: UUID
    material_name: str

    supplier_id: UUID
    supplier_name: str

    quantity: Decimal
    estimated_cost: Decimal

    lead_time_days: int

    status: PurchasePlanStatus
    priority: ProcurementPriority

class ProcurementSummary(BaseModel):
    draft_purchase_plans: int = Field(ge=0)
    approved_purchase_plans: int = Field(ge=0)

    pending_purchase_plans: int = Field(ge=0)

    materials_to_replenish: int = Field(ge=0)

    estimated_pending_cost: Decimal = Field(ge=0)

    critical_materials: int = Field(ge=0)

    top_actions: list[ProcurementAction]


# ============================================================
# Production Risks
# ============================================================


class ProductionRiskOverviewItem(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str

    current_producible_units: Decimal
    risk_level: ProductionRiskLevel

    bottleneck_material_name: str | None

class ProductionRiskSummary(BaseModel):
    products_analyzed: int = Field(ge=0)

    low_risk_products: int = Field(ge=0)
    medium_risk_products: int = Field(ge=0)
    high_risk_products: int = Field(ge=0)
    critical_risk_products: int = Field(ge=0)

    top_risks: list[ProductionRiskOverviewItem]


# ============================================================
# Material Coverage
# ============================================================


class MaterialCoverageRisk(BaseModel):
    material_id: UUID
    material_name: str
    material_sku: str

    current_stock: Decimal
    average_daily_consumption: Decimal

    days_of_stock: Decimal | None

    status: MaterialCoverageStatus


class MaterialCoverageSummary(BaseModel):
    materials_tracked: int

    critical_materials: int
    low_coverage_materials: int

    average_days_of_stock: Decimal | None
    minimum_days_of_stock: Decimal | None

    top_risks: list[MaterialCoverageRisk]


# ============================================================
# Supplier Risk
# ============================================================


class SupplierRiskOverviewItem(BaseModel):
    supplier_id: UUID
    supplier_name: str

    lead_time_days: int

    affected_materials: int
    critical_materials: int
    high_risk_materials: int

    risk_level: RiskLevel

class SupplierRiskSummary(BaseModel):
    total_suppliers: int

    suppliers_at_risk: int

    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int

    top_risks: list[SupplierRiskOverviewItem]


# ============================================================
# Dashboard Overview
# ============================================================


class DashboardOverviewResponse(BaseModel):
    operational_health: OperationalHealth

    production_readiness: ProductionReadiness

    inventory_health: InventoryHealth

    procurement: ProcurementSummary

    production_risks: ProductionRiskSummary

    material_coverage: MaterialCoverageSummary

    supplier_risk: SupplierRiskSummary