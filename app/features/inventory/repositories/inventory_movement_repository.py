from uuid import UUID

from sqlalchemy import delete, select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory_movement import (
    InventoryMovementTable
)
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.schema import InventoryMovementFilterSchema


class InventoryMovementRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def count(
        self,
        filters: InventoryMovementFilterSchema,
    ) -> int:

        statement = (
            self._build_filtered_statement(filters)
            .with_only_columns(func.count())
            .order_by(None)
        )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def get(
        self,
        filters: InventoryMovementFilterSchema,
        offset: int = 0,
        limit: int = 20,
    ) -> list[InventoryMovementTable]:

        statement = (
            self._build_filtered_statement(filters)
            .order_by(
                InventoryMovementTable.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def save(
        self,
        movement: InventoryMovementTable,
    ) -> InventoryMovementTable:
        self.session.add(movement)

        await self.session.commit()
        await self.session.refresh(movement)

        return movement

    async def get_by_id(
        self,
        movement_id: UUID,
    ) -> InventoryMovementTable | None:

        statement = select(
            InventoryMovementTable
        ).where(
            InventoryMovementTable.id == movement_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_inventory_id(
        self,
        inventory_id: UUID,
    ) -> list[InventoryMovementTable]:

        statement = (
            select(InventoryMovementTable)
            .where(
                InventoryMovementTable.inventory_id == inventory_id
            )
            .order_by(
                InventoryMovementTable.created_at.desc()
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def delete(
        self,
        movement_id: UUID,
    ) -> bool:

        statement = delete(
            InventoryMovementTable
        ).where(
            InventoryMovementTable.id == movement_id
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    def _build_filtered_statement(
        self,
        filters: InventoryMovementFilterSchema,
    ):
        statement = select(InventoryMovementTable)

        needs_inventory_join = (
            filters.owner_type is not None
            or filters.owner_id is not None
        )

        if needs_inventory_join:
            statement = statement.join(
                InventoryTable,
                InventoryMovementTable.inventory_id == InventoryTable.id,
            )

        if filters.owner_type:
            statement = statement.where(
                InventoryTable.owner_type == filters.owner_type
            )

        if filters.owner_id:
            statement = statement.where(
                InventoryTable.owner_id == filters.owner_id
            )

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    InventoryMovementTable.owner_name.ilike(search),
                    InventoryMovementTable.owner_code.ilike(search),
                )
            )

        if filters.movement_type:
            statement = statement.where(
                InventoryMovementTable.movement_type == filters.movement_type
            )

        if filters.created_from:
            statement = statement.where(
                InventoryMovementTable.created_at >= filters.created_from
            )

        if filters.created_to:
            statement = statement.where(
                InventoryMovementTable.created_at <= filters.created_to
            )

        return statement