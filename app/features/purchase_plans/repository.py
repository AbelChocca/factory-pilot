from uuid import UUID

from sqlalchemy import delete, select, func, cast, String
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.purchase_plans.model import (
    PurchasePlanItemTable,
    PurchasePlanTable,
)
from app.features.purchase_plans.types import PurchasePlanStatus
from app.features.purchase_plans.model import PurchasePlanItemTable
from app.features.purchase_plans.schema import PurchasePlanItem
from app.features.suppliers.models.supplier import SupplierTable
from app.features.materials.model import MaterialTable


class PurchasePlanRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_all(
        self,
        page: int,
        limit: int,
        search: str | None = None
    ) -> tuple[list[PurchasePlanTable], int]:

        offset = (page - 1) * limit

        count_statement = select(
            func.count(PurchasePlanTable.id)
        )

        if search is not None:
            count_statement = count_statement.where(
                cast(PurchasePlanTable.id, String).ilike(f"%{search}%")
            )

        total_result = await self.session.execute(count_statement)

        total_items = total_result.scalar_one()

        statement = (
            select(PurchasePlanTable)
            .options(
                noload(PurchasePlanTable.items)
            )
        )

        if search is not None:
            statement = statement.where(
                cast(PurchasePlanTable.id, String).ilike(f"%{search}%")
            )

        statement = (
            statement
            .order_by(PurchasePlanTable.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        purchase_plans = result.scalars().all()

        return list(purchase_plans), total_items

    async def get_items(
        self,
        purchase_plan_id: UUID,
    ) -> list[PurchasePlanItem]:

        statement = (
            select(
                PurchasePlanItemTable,
                MaterialTable,
                SupplierTable,
            )
            .join(
                MaterialTable,
                MaterialTable.id == PurchasePlanItemTable.material_id,
            )
            .join(
                SupplierTable,
                SupplierTable.id == PurchasePlanItemTable.supplier_id,
            )
            .where(
                PurchasePlanItemTable.purchase_plan_id
                == purchase_plan_id,
            )
        )

        result = await self.session.execute(statement)

        return [
            PurchasePlanItem(
                material_id=item.material_id,
                material_name=material.name,
                supplier_id=item.supplier_id,
                supplier_name=supplier.name,
                quantity=item.quantity,
                unit_type=material.unit_type,
                unit_price=item.unit_price,
                estimated_cost=item.estimated_cost,
                lead_time_days=item.lead_time_days,
                preferred_supplier=item.preferred_supplier,
            )
            for item, material, supplier in result.all()
        ]

    async def save(
        self,
        purchase_plan: PurchasePlanTable,
    ) -> PurchasePlanTable:

        self.session.add(purchase_plan)

        await self.session.commit()
        await self.session.refresh(purchase_plan)

        return purchase_plan

    async def get_by_id(
        self,
        purchase_plan_id: UUID,
    ) -> PurchasePlanTable | None:

        statement = (
            select(PurchasePlanTable)
            .where(
                PurchasePlanTable.id == purchase_plan_id,
            )
            .options(
                selectinload(
                    PurchasePlanTable.items,
                ),
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_current(
        self,
    ) -> PurchasePlanTable | None:

        statement = (
            select(PurchasePlanTable)
            .where(
                PurchasePlanTable.status
                == PurchasePlanStatus.DRAFT,
            )
            .order_by(
                PurchasePlanTable.created_at.desc(),
            )
            .options(
                selectinload(
                    PurchasePlanTable.items,
                ),
            )
            .limit(1)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def update(
        self,
        purchase_plan: PurchasePlanTable,
    ) -> PurchasePlanTable:

        await self.session.commit()

        await self.session.refresh(
            purchase_plan,
        )

        return purchase_plan

    async def replace_items(
        self,
        purchase_plan: PurchasePlanTable,
        items: list[PurchasePlanItemTable],
    ) -> PurchasePlanTable:

        await self.session.execute(
            delete(PurchasePlanItemTable).where(
                PurchasePlanItemTable.purchase_plan_id
                == purchase_plan.id,
            )
        )

        self.session.add_all(items)

        self.session.add(purchase_plan)

        await self.session.commit()

        await self.session.refresh(
            purchase_plan,
        )

        return purchase_plan

    async def delete_item(
        self,
        item_id: UUID,
    ) -> bool:

        statement = delete(
            PurchasePlanItemTable,
        ).where(
            PurchasePlanItemTable.id == item_id,
        )

        result = await self.session.execute(
            statement,
        )

        return result.rowcount > 0

    async def add_item(
        self,
        item: PurchasePlanItemTable,
    ) -> PurchasePlanItemTable:

        self.session.add(item)

        await self.session.commit()

        await self.session.refresh(item)

        return item

    async def delete(
        self,
        purchase_plan_id: UUID,
    ) -> bool:

        statement = delete(
            PurchasePlanTable,
        ).where(
            PurchasePlanTable.id == purchase_plan_id,
        )

        result = await self.session.execute(
            statement,
        )

        return result.rowcount > 0