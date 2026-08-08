from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.features.production_risk.repository import (
    ProductionAnalysisRepository,
)
from app.features.production_risk.production_risk_schema import (
    ProductionRiskAnalysisSchema,
    ProductionRiskFactorSchema,
    ProductionRiskMaterialSchema,
    ProductionRiskProductSchema,
    ProductionRiskSupplierSchema,
    ProductionRiskLLMFactorSchema,
    ProductionRiskLLMContextSchema,
    ProductionRiskLLMProductSchema,
    ProductionRiskLLMMaterialSchema
)
from app.features.production_risk.production_risk_types import (
    ConsumptionTrend,
    ProductionRiskFactorType,
    ProductionRiskLevel,
)
from app.features.inventory.types import AvailabilityStatus

class ProductionRiskAnalyzer:

    ANALYSIS_PERIOD_DAYS = 30

    def __init__(
        self,
        repository: ProductionAnalysisRepository,
    ):
        self.repository = repository

    def to_llm_context(
        self,
        analysis: ProductionRiskAnalysisSchema,
    ) -> ProductionRiskLLMContextSchema:

        products = []

        for product in analysis.products:

            bottleneck = product.bottleneck_material

            material = ProductionRiskLLMMaterialSchema(
                material_id=bottleneck.material_id,
                material_name=bottleneck.material_name,
                current_stock=bottleneck.current_stock,
                minimum_stock=bottleneck.minimum_stock,
                required_per_product=(
                    bottleneck.required_per_product
                ),
                producible_units=(
                    bottleneck.producible_units
                ),
                average_daily_consumption=(
                    bottleneck.average_daily_consumption
                ),
                days_of_stock=bottleneck.days_of_stock,
            )

            factors = [
                ProductionRiskLLMFactorSchema(
                    factor=factor.factor,
                    severity=factor.severity,
                    owner_id=factor.owner_id,
                    owner_name=factor.owner_name,
                    value=factor.value,
                    description=factor.description,
                )
                for factor in product.risk_factors
            ]

            products.append(
                ProductionRiskLLMProductSchema(
                    product_id=product.product_id,
                    product_name=product.product_name,
                    product_sku=product.product_sku,
                    risk_level=product.risk_level,
                    current_producible_units=(
                        product.current_producible_units
                    ),
                    bottleneck_material=material,
                    risk_factors=factors,
                )
            )

        return ProductionRiskLLMContextSchema(
            analysis_period_days=analysis.analysis_period_days,
            products_analyzed=analysis.products_analyzed,
            high_risk_products=analysis.high_risk_products,
            medium_risk_products=analysis.medium_risk_products,
            low_risk_products=analysis.low_risk_products,
            products=products,
        )

    async def execute(
        self,
    ) -> ProductionRiskAnalysisSchema:

        product_materials = (
            await self.repository.get_product_materials()
        )

        if not product_materials:
            return ProductionRiskAnalysisSchema(
                analysis_period_days=self.ANALYSIS_PERIOD_DAYS,
                products_analyzed=0,
                high_risk_products=0,
                medium_risk_products=0,
                low_risk_products=0,
                products=[],
            )

        material_ids = list({
            row.material_id
            for row in product_materials
        })

        inventory = (
            await self.repository.get_material_inventory(
                material_ids,
            )
        )

        since = (
            datetime.now(timezone.utc)
            - timedelta(days=self.ANALYSIS_PERIOD_DAYS)
        )

        movements = (
            await self.repository.get_material_movement_summary(
                material_ids,
                since,
            )
        )

        suppliers = (
            await self.repository.get_material_suppliers(
                material_ids,
            )
        )

        inventory_by_material = {
            row.material_id: row
            for row in inventory
        }

        movements_by_material = {
            row.material_id: row
            for row in movements
        }

        suppliers_by_material: dict[
            UUID,
            list,
        ] = {}

        for supplier in suppliers:
            suppliers_by_material.setdefault(
                supplier.material_id,
                [],
            ).append(supplier)

        products = self._build_products(
            product_materials=product_materials,
            inventory_by_material=inventory_by_material,
            movements_by_material=movements_by_material,
            suppliers_by_material=suppliers_by_material,
        )

        risk_products = [
            product
            for product in products
            if product.risk_level != ProductionRiskLevel.LOW
        ]

        return ProductionRiskAnalysisSchema(
            analysis_period_days=self.ANALYSIS_PERIOD_DAYS,
            products_analyzed=len(products),
            high_risk_products=sum(
                product.risk_level in {
                    ProductionRiskLevel.HIGH,
                    ProductionRiskLevel.CRITICAL,
                }
                for product in products
            ),
            medium_risk_products=sum(
                product.risk_level
                == ProductionRiskLevel.MEDIUM
                for product in products
            ),
            low_risk_products=sum(
                product.risk_level
                == ProductionRiskLevel.LOW
                for product in products
            ),
            products=risk_products,
        )

    def _build_products(
        self,
        product_materials,
        inventory_by_material,
        movements_by_material,
        suppliers_by_material,
    ) -> list[ProductionRiskProductSchema]:

        grouped: dict[UUID, list] = {}

        for row in product_materials:
            grouped.setdefault(
                row.product_id,
                [],
            ).append(row)

        products = []

        for product_rows in grouped.values():

            risk_materials = []

            for row in product_rows:
                inventory = inventory_by_material.get(
                    row.material_id,
                )

                movement = movements_by_material.get(
                    row.material_id,
                )

                material_suppliers = (
                    suppliers_by_material.get(
                        row.material_id,
                        [],
                    )
                )

                risk_material = self._build_material_risk(
                    row=row,
                    inventory=inventory,
                    movement=movement,
                    suppliers=material_suppliers,
                )

                risk_materials.append(
                    risk_material,
                )

            bottleneck = min(
                risk_materials,
                key=lambda material: material.producible_units,
            )

            current_producible_units = (
                bottleneck.producible_units
            )

            risk_factors = []

            for material in risk_materials:
                risk_factors.extend(
                    self._build_risk_factors(
                        material,
                    )
                )

            risk_level = self._calculate_risk_level(
                risk_factors,
            )

            products.append(
                ProductionRiskProductSchema(
                    product_id=product_rows[0].product_id,
                    product_name=product_rows[0].product_name,
                    product_sku=product_rows[0].product_sku,
                    current_producible_units=(
                        current_producible_units
                    ),
                    risk_level=risk_level,
                    risk_factors=risk_factors,
                    bottleneck_material=bottleneck,
                    risk_materials=risk_materials,
                )
            )

        return products

    def _build_material_risk(
        self,
        row,
        inventory,
        movement,
        suppliers,
    ) -> ProductionRiskMaterialSchema:

        current_stock = (
            inventory.quantity
            if inventory
            else Decimal("0")
        )

        minimum_stock = (
            inventory.minimum_quantity
            if inventory
            else Decimal("0")
        )

        average_daily_consumption = (
            self._calculate_average_daily_consumption(
                movement,
            )
        )

        days_of_stock = (
            self._calculate_days_of_stock(
                current_stock,
                average_daily_consumption,
            )
        )

        producible_units = (
            self._calculate_producible_units(
                current_stock,
                row.required_quantity,
            )
        )

        consumption_trend = (
            self._calculate_consumption_trend(
                movement,
            )
        )

        stock_status = self._calculate_stock_status(
            current_stock=current_stock,
            minimum_stock=minimum_stock,
        )

        return ProductionRiskMaterialSchema(
            material_id=row.material_id,
            material_name=row.material_name,
            material_sku=row.material_sku,
            unit_type=row.material_unit_type,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            required_per_product=row.required_quantity,
            producible_units=producible_units,
            average_daily_consumption=(
                average_daily_consumption
            ),
            days_of_stock=days_of_stock,
            stock_status=stock_status,
            consumption_trend=consumption_trend,
            suppliers=[
                ProductionRiskSupplierSchema(
                    supplier_id=supplier.supplier_id,
                    supplier_name=supplier.supplier_name,
                    lead_time_days=supplier.lead_time_days,
                    unit_price=supplier.unit_price,
                    preferred=supplier.preferred,
                )
                for supplier in suppliers
            ],
        )

    def _calculate_average_daily_consumption(
        self,
        movement,
    ) -> Decimal:

        if not movement:
            return Decimal("0")

        return (
            movement.total_outbound
            / Decimal(str(self.ANALYSIS_PERIOD_DAYS))
        )

    def _calculate_days_of_stock(
        self,
        current_stock: Decimal,
        average_daily_consumption: Decimal,
    ) -> Decimal | None:

        if average_daily_consumption <= 0:
            return None

        return (
            current_stock
            / average_daily_consumption
        ).quantize(
            Decimal("0.01")
        )

    def _calculate_producible_units(
        self,
        current_stock: Decimal,
        required_quantity: Decimal,
    ) -> Decimal:

        if required_quantity <= 0:
            return Decimal("0")

        return (
            current_stock
            / required_quantity
        ).quantize(
            Decimal("0.01")
        )

    def _calculate_stock_status(
        self,
        current_stock: Decimal,
        minimum_stock: Decimal,
    ) -> AvailabilityStatus:

        if current_stock <= 0:
            return AvailabilityStatus.OUT_OF_STOCK

        if current_stock <= minimum_stock:
            return AvailabilityStatus.LOW_STOCK

        return AvailabilityStatus.AVAILABLE

    def _calculate_consumption_trend(
        self,
        movement,
    ) -> ConsumptionTrend:

        if not movement:
            return ConsumptionTrend.STABLE

        if movement.total_outbound <= 0:
            return ConsumptionTrend.STABLE
        
        return ConsumptionTrend.STABLE

    def _build_risk_factors(
        self,
        material: ProductionRiskMaterialSchema,
    ) -> list[ProductionRiskFactorSchema]:

        factors = []

        if (
            material.stock_status
            == AvailabilityStatus.OUT_OF_STOCK
        ):
            factors.append(
                ProductionRiskFactorSchema(
                    factor=ProductionRiskFactorType.LOW_STOCK,
                    severity=ProductionRiskLevel.CRITICAL,
                    value=material.current_stock,
                    owner_id=material.material_id,
                    owner_name=material.material_name,
                    description=(
                        "Material is currently out of stock."
                    ),
                )
            )

        elif (
            material.stock_status
            == AvailabilityStatus.LOW_STOCK
        ):
            factors.append(
                ProductionRiskFactorSchema(
                    factor=ProductionRiskFactorType.LOW_STOCK,
                    severity=ProductionRiskLevel.HIGH,
                    value=material.current_stock,
                    owner_id=material.material_id,
                    owner_name=material.material_name,
                    description=(
                        "Material stock is below "
                        "the minimum required level."
                    ),
                )
            )

        if (
            material.days_of_stock is not None
            and material.days_of_stock <= 3
        ):
            factors.append(
                ProductionRiskFactorSchema(
                    factor=(
                        ProductionRiskFactorType
                        .LOW_STOCK_COVERAGE
                    ),
                    severity=ProductionRiskLevel.CRITICAL,
                    value=material.days_of_stock,
                    owner_id=material.material_id,
                    owner_name=material.material_name,
                    description=(
                        "Current stock covers "
                        "three days or less of "
                        "average consumption."
                    ),
                )
            )

        if material.producible_units <= 5:
            factors.append(
                ProductionRiskFactorSchema(
                    factor=(
                        ProductionRiskFactorType
                        .PRODUCTION_BOTTLENECK
                    ),
                    severity=ProductionRiskLevel.HIGH,
                    value=material.producible_units,
                    owner_id=material.material_id,
                    owner_name=material.material_name,
                    description=(
                        "Material significantly "
                        "limits the number of units "
                        "that can currently be produced."
                    ),
                )
            )

        if not material.suppliers:
            factors.append(
                ProductionRiskFactorSchema(
                    factor=(
                        ProductionRiskFactorType
                        .NO_SUPPLIER
                    ),
                    severity=ProductionRiskLevel.CRITICAL,
                    value=None,
                    owner_id=material.material_id,
                    owner_name=material.material_name,
                    description=(
                        "No active supplier is available "
                        "for this material."
                    ),
                )
            )

        elif material.days_of_stock is not None:

            supplier = min(
                material.suppliers,
                key=lambda supplier: supplier.lead_time_days,
            )

            if supplier.lead_time_days > material.days_of_stock:
                factors.append(
                    ProductionRiskFactorSchema(
                        factor=(
                            ProductionRiskFactorType
                            .SUPPLIER_LEAD_TIME
                        ),
                        severity=ProductionRiskLevel.HIGH,
                        value=Decimal(
                            str(supplier.lead_time_days)
                        ),
                        owner_id=supplier.supplier_id,
                        owner_name=supplier.supplier_name,
                        description=(
                            "The shortest supplier lead "
                            "time exceeds the remaining "
                            "stock coverage."
                        ),
                    )
                )

        return factors

    def _calculate_risk_level(
        self,
        factors: list[ProductionRiskFactorSchema],
    ) -> ProductionRiskLevel:

        if any(
            factor.severity
            == ProductionRiskLevel.CRITICAL
            for factor in factors
        ):
            return ProductionRiskLevel.CRITICAL

        high_count = sum(
            factor.severity
            == ProductionRiskLevel.HIGH
            for factor in factors
        )

        if high_count >= 2:
            return ProductionRiskLevel.HIGH

        if high_count == 1:
            return ProductionRiskLevel.MEDIUM

        return ProductionRiskLevel.LOW

    