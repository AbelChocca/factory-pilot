from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType
from app.features.materials.model import MaterialTable

class InventoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_owner(
        self,
        owner_type: InventoryOwnerType,
        owner_id: UUID,
    ) -> InventoryTable | None:
        statement = select(InventoryTable).where(
            InventoryTable.owner_type == owner_type,
            InventoryTable.owner_id == owner_id,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def save(
        self,
        inventory: InventoryTable,
    ) -> InventoryTable:
        self.session.add(inventory)

        await self.session.commit()
        await self.session.refresh(inventory)

        return inventory

    async def get_by_id(
        self,
        inventory_id: UUID,
    ) -> InventoryTable | None:
        statement = select(InventoryTable).where(
            InventoryTable.id == inventory_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def update_quantity(
        self,
        owner_type: InventoryOwnerType,
        owner_id: UUID,
        quantity: Decimal,
    ) -> bool:
        statement = (
            update(InventoryTable)
            .where(
                InventoryTable.owner_type == owner_type,
                InventoryTable.owner_id == owner_id,
            )
            .values(
                quantity=quantity,
                updated_at=datetime.now(timezone.utc),
                last_movement_at=datetime.now(timezone.utc),
            )
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    async def delete(
        self,
        inventory_id: UUID,
    ) -> bool:
        statement = delete(InventoryTable).where(
            InventoryTable.id == inventory_id
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    async def get_low_stock_materials(
        self,
    ) -> list[tuple[InventoryTable, MaterialTable]]:

        statement = (
            select(
                InventoryTable,
                MaterialTable,
            )
            .join(
                MaterialTable,
                InventoryTable.owner_id == MaterialTable.id,
            )
            .where(
                InventoryTable.owner_type == InventoryOwnerType.MATERIAL,
                InventoryTable.quantity < InventoryTable.minimum_quantity,
            )
        )

        result = await self.session.execute(statement)

        return list(result.all())