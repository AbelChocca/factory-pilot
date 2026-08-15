from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType
from app.features.purchase_plans.model import PurchasePlanTable
from app.features.purchase_plans.types import PurchasePlanStatus
from app.features.materials.model import MaterialTable


class OperationalHealthRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def count_materials(self) -> int:
        statement = (
            select(func.count(MaterialTable.id))
        )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def get_inventory_status_counts(
        self,
    ) -> tuple[int, int]:

        statement = select(
            func.count().filter(
                InventoryTable.quantity > 0,
                InventoryTable.quantity
                <= InventoryTable.minimum_quantity,
            ),
            func.count().filter(
                InventoryTable.quantity <= 0,
            ),
        ).where(
            InventoryTable.owner_type == InventoryOwnerType.MATERIAL,
        )

        result = await self.session.execute(statement)

        low_stock, out_of_stock = result.one()

        return low_stock, out_of_stock

    async def count_pending_purchase_plans(self) -> int:
        statement = (
            select(func.count(PurchasePlanTable.id))
            .where(
                PurchasePlanTable.status.in_(
                    [
                        PurchasePlanStatus.DRAFT
                    ]
                )
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one()