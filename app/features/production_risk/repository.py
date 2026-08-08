from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory import (
    InventoryTable
)
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.features.materials.model import MaterialTable
from app.features.products.models.product import (
    ProductTable
)
from app.features.products.models.product_material import ProductMaterialTable
from app.features.suppliers.models.supplier import (
    SupplierTable
)
from app.features.suppliers.models.supplier_material import SupplierMaterialTable
from app.features.production_risk.production_risk_schema import (
    MaterialMovementSummaryRow,
    ProductMaterialAnalysisRow,
    MaterialSupplierAnalysisRow,
    MaterialInventoryAnalysisRow
)
from app.features.inventory.types import InventoryOwnerType, InventoryMovementType
from app.shared.enums import Status


class ProductionAnalysisRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_material_by_id(
            self,
            material_id: UUID
    ) -> MaterialTable:
        stmt = select(MaterialTable).where(MaterialTable.id == material_id)

        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_product_materials(
        self,
        product_ids: list[UUID] | None = None,
        material_ids: list[UUID] | None = None,
    ) -> list[ProductMaterialAnalysisRow]:

        statement = (
            select(
                ProductTable.id,
                ProductTable.name,
                ProductTable.sku,

                MaterialTable.id,
                MaterialTable.name,
                MaterialTable.sku,
                MaterialTable.unit_type,

                ProductMaterialTable.quantity,
            )
            .join(
                ProductMaterialTable,
                ProductMaterialTable.product_id
                == ProductTable.id,
            )
            .join(
                MaterialTable,
                MaterialTable.id
                == ProductMaterialTable.material_id,
            )
        )

        if product_ids:
            statement = statement.where(
                ProductTable.id.in_(product_ids)
            )

        if material_ids:
            statement = statement.where(
                MaterialTable.id.in_(material_ids)
            )

        result = await self.session.execute(statement)

        return [
            ProductMaterialAnalysisRow(
                product_id=product_id,
                product_name=product_name,
                product_sku=product_sku,

                material_id=material_id,
                material_name=material_name,
                material_sku=material_sku,
                material_unit_type=unit_type,

                required_quantity=required_quantity,
            )
            for (
                product_id,
                product_name,
                product_sku,
                material_id,
                material_name,
                material_sku,
                unit_type,
                required_quantity,
            ) in result.all()
        ]

    async def get_material_inventory(
        self,
        material_ids: list[UUID],
    ) -> list[MaterialInventoryAnalysisRow]:

        statement = (
            select(
                InventoryTable.owner_id,
                InventoryTable.quantity,
                InventoryTable.minimum_quantity,
            )
            .where(
                InventoryTable.owner_type == InventoryOwnerType.MATERIAL,
                InventoryTable.owner_id.in_(material_ids),
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialInventoryAnalysisRow(
                material_id=material_id,
                quantity=quantity,
                minimum_quantity=minimum_quantity,
            )
            for (
                material_id,
                quantity,
                minimum_quantity,
            ) in result.all()
        ]

    async def get_material_movement_summary(
        self,
        material_ids: list[UUID],
        since: datetime,
    ) -> list[MaterialMovementSummaryRow]:

        statement = (
            select(
                InventoryTable.owner_id,

                func.coalesce(
                    func.sum(
                        case(
                            (
                                InventoryMovementTable.movement_type
                                == InventoryMovementType.IN,
                                InventoryMovementTable.quantity,
                            ),
                            else_=Decimal("0"),
                        )
                    ),
                    Decimal("0"),
                ).label("total_inbound"),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                InventoryMovementTable.movement_type
                                == InventoryMovementType.OUT,
                                InventoryMovementTable.quantity,
                            ),
                            else_=Decimal("0"),
                        )
                    ),
                    Decimal("0"),
                ).label("total_outbound"),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                InventoryMovementTable.movement_type
                                == InventoryMovementType.ADJUSTMENT,
                                InventoryMovementTable.quantity,
                            ),
                            else_=Decimal("0"),
                        )
                    ),
                    Decimal("0"),
                ).label("total_adjustments"),

                func.count(
                    case(
                        (
                            InventoryMovementTable.movement_type
                            == InventoryMovementType.OUT,
                            1,
                        )
                    )
                ).label("outbound_movements"),
            )
            .join(
                InventoryTable,
                InventoryTable.id
                == InventoryMovementTable.inventory_id,
            )
            .where(
                InventoryTable.owner_type
                == InventoryOwnerType.MATERIAL,
                InventoryTable.owner_id.in_(material_ids),
                InventoryMovementTable.created_at >= since,
            )
            .group_by(
                InventoryTable.owner_id,
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialMovementSummaryRow(
                material_id=material_id,
                total_inbound=total_inbound,
                total_outbound=total_outbound,
                total_adjustments=total_adjustments,
                outbound_movements=outbound_movements,
            )
            for (
                material_id,
                total_inbound,
                total_outbound,
                total_adjustments,
                outbound_movements,
            ) in result.all()
        ]

    async def get_material_suppliers(
        self,
        material_ids: list[UUID],
    ) -> list[MaterialSupplierAnalysisRow]:

        statement = (
            select(
                SupplierMaterialTable.material_id,

                SupplierTable.id,
                SupplierTable.name,
                SupplierTable.lead_time_days,

                SupplierMaterialTable.unit_price,
                SupplierMaterialTable.preferred,
            )
            .join(
                SupplierTable,
                SupplierTable.id
                == SupplierMaterialTable.supplier_id,
            )
            .where(
                SupplierMaterialTable.material_id.in_(material_ids),
                SupplierTable.status == Status.ACTIVE,
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialSupplierAnalysisRow(
                material_id=material_id,
                supplier_id=supplier_id,
                supplier_name=supplier_name,
                lead_time_days=lead_time_days,
                unit_price=unit_price,
                preferred=preferred,
            )
            for (
                material_id,
                supplier_id,
                supplier_name,
                lead_time_days,
                unit_price,
                preferred,
            ) in result.all()
        ]