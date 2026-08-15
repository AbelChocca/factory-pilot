from decimal import Decimal
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.materials.model import MaterialTable
from app.features.suppliers.models.supplier import SupplierTable

from app.features.purchase_plans.model import (
    PurchasePlanItemTable,
    PurchasePlanTable,
)
from app.features.purchase_plans.types import (
    PurchasePlanStatus,
)

@dataclass
class ProcurementItemRow:
    purchase_plan_id: UUID
    purchase_plan_status: PurchasePlanStatus

    material_id: UUID
    material_name: str

    supplier_id: UUID
    supplier_name: str

    quantity: Decimal
    estimated_cost: Decimal
    lead_time_days: int


class ProcurementRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def count_by_status(
        self,
        status: PurchasePlanStatus,
    ) -> int:

        statement = select(
            func.count(PurchasePlanTable.id)
        ).where(
            PurchasePlanTable.status == status,
        )

        result = await self.session.execute(
            statement,
        )

        return result.scalar_one()

    async def get_pending_cost(self) -> Decimal:

        statement = select(
            func.coalesce(
                func.sum(
                    PurchasePlanTable.total_estimated_cost
                ),
                0,
            )
        ).where(
            PurchasePlanTable.status.in_(
                [
                    PurchasePlanStatus.DRAFT,
                    PurchasePlanStatus.APPROVED
                ]
            )
        )

        result = await self.session.execute(
            statement,
        )

        return result.scalar_one()

    async def get_pending_items(
        self,
    ) -> list[ProcurementItemRow]:

        statement = (
            select(
                PurchasePlanItemTable.purchase_plan_id,
                PurchasePlanTable.status.label(
                    "purchase_plan_status",
                ),

                MaterialTable.id.label(
                    "material_id",
                ),
                MaterialTable.name.label(
                    "material_name",
                ),

                SupplierTable.id.label(
                    "supplier_id",
                ),
                SupplierTable.name.label(
                    "supplier_name",
                ),

                PurchasePlanItemTable.quantity,
                PurchasePlanItemTable.estimated_cost,
                PurchasePlanItemTable.lead_time_days,
            )
            .join(
                PurchasePlanTable,
                PurchasePlanTable.id
                == PurchasePlanItemTable.purchase_plan_id,
            )
            .join(
                MaterialTable,
                MaterialTable.id
                == PurchasePlanItemTable.material_id,
            )
            .join(
                SupplierTable,
                SupplierTable.id
                == PurchasePlanItemTable.supplier_id,
            )
            .where(
                PurchasePlanTable.status.in_(
                    [
                        PurchasePlanStatus.DRAFT,
                        PurchasePlanStatus.APPROVED,
                    ]
                )
            )
            .order_by(
                PurchasePlanItemTable.estimated_cost.desc(),
            )
        )

        result = await self.session.execute(
            statement,
        )

        rows = result.all()

        return [
            ProcurementItemRow(
                purchase_plan_id=row.purchase_plan_id,
                purchase_plan_status=row.purchase_plan_status,
                material_id=row.material_id,
                material_name=row.material_name,
                supplier_id=row.supplier_id,
                supplier_name=row.supplier_name,
                quantity=row.quantity,
                estimated_cost=row.estimated_cost,
                lead_time_days=row.lead_time_days,
            )
            for row in rows
        ]