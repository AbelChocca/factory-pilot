from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.suppliers.models.supplier import SupplierTable
from app.features.suppliers.schemas.supplier import SupplierFilterSchema


class SupplierRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(
        self,
        filters: SupplierFilterSchema,
    ) -> int:
        statement = select(func.count()).select_from(SupplierTable)

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    SupplierTable.name.ilike(search),
                    SupplierTable.email.ilike(search),
                    SupplierTable.phone.ilike(search),
                )
            )

        if filters.status:
            statement = statement.where(
                SupplierTable.status == filters.status
            )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def save(
        self,
        supplier: SupplierTable,
    ) -> SupplierTable:
        self.session.add(supplier)

        await self.session.commit()
        await self.session.refresh(supplier)

        return supplier

    async def get_by_id(
        self,
        supplier_id: UUID,
    ) -> SupplierTable | None:
        statement = select(SupplierTable).where(
            SupplierTable.id == supplier_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get(
        self,
        filters: SupplierFilterSchema,
        offset: int = 0,
        limit: int = 20,
    ):
        statement = select(SupplierTable)

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    SupplierTable.name.ilike(search),
                    SupplierTable.email.ilike(search),
                    SupplierTable.phone.ilike(search),
                )
            )

        if filters.status:
            statement = statement.where(
                SupplierTable.status == filters.status
            )

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def delete_by_id(
        self,
        supplier_id: UUID,
    ) -> bool:
        statement = delete(SupplierTable).where(
            SupplierTable.id == supplier_id
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0