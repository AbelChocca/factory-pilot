from pydantic import BaseModel, Field
from typing import Annotated, Literal
from uuid import UUID
from enum import StrEnum
from decimal import Decimal

from app.features.suppliers.schemas.supplier_material import MaterialSupplierDetailResponse
from app.features.purchase_plans.schema import PurchasePlanItem
from app.features.inventory.schema import LowStockMaterial
from app.features.production_risk.production_risk_schema import ProductionRiskLLMProductSchema
from app.features.production_risk.production_risk_types import (
    MaterialImpactLevel,
)

class SuggestedAction(StrEnum):
    GENERATE_PURCHASE_PLAN = "generate_purchase_plan"
    VIEW_SUPPLIERS = "view_suppliers"

class MaterialImpactAnalysisEvent(BaseModel):
    type: Literal["material_impact_analysis"] = (
        "material_impact_analysis"
    )
    
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

class ProductionRiskAnalysisEvent(BaseModel):
    type: Literal["production_risk_analysis"] = (
        "production_risk_analysis"
    )

    analysis_period_days: int
    products_analyzed: int
    high_risk_products: int
    medium_risk_products: int
    low_risk_products: int

    products: list[ProductionRiskLLMProductSchema]

class PurchasePlanApprovedEvent(BaseModel):
    type: Literal["purchase_plan_approved"] = (
        "purchase_plan_approved"
    )

    purchase_plan_id: UUID
    items: list[PurchasePlanItem]
    total_estimated_cost: float

class LowStockMaterialEvent(BaseModel):
    type: Literal["low_stock_materials"] = "low_stock_materials"
    materials: list[LowStockMaterial]

class SupplierRecommendationEvent(BaseModel):
    type: Literal["supplier_recommendations"] = "supplier_recommendations"
    materials: list[MaterialSupplierDetailResponse]


class SuggestedActionEvent(BaseModel):
    type: Literal["suggested_action"] = "suggested_action"
    action: SuggestedAction
    label: str

class PurchasePlanEvent(BaseModel):
    type: Literal["purchase_plan"] = "purchase_plan"
    purchase_plan_id: UUID
    items: list[PurchasePlanItem]
    total_estimated_cost: float

class PurchasePlanUpdatedEvent(BaseModel):
    type: Literal["purchase_plan_updated"] = "purchase_plan_updated"
    purchase_plan_id: UUID
    items: list[PurchasePlanItem]
    total_estimated_cost: float

class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


AIEvent = Annotated[
    (
        LowStockMaterialEvent
        | SupplierRecommendationEvent
        | SuggestedActionEvent
        | PurchasePlanEvent
        | PurchasePlanUpdatedEvent
        | PurchasePlanApprovedEvent
        | ProductionRiskAnalysisEvent
        | MaterialImpactAnalysisEvent
        | ErrorEvent
    ),
    Field(discriminator="type"),
]


class AIChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None

class AIChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    events: list[AIEvent] = Field(default_factory=list)