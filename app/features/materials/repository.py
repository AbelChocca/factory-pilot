from uuid import UUID

from sqlalchemy import delete, select, or_, and_, func
from sqlmodel import col
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.materials.model import MaterialTable
from app.features.materials.schema import MaterialFilterSchema
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import AvailabilityStatus, InventoryOwnerType

class MaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count(
        self,
        filters: MaterialFilterSchema,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(MaterialTable)
            .join(
                InventoryTable,
                and_(
                    InventoryTable.owner_type == InventoryOwnerType.MATERIAL,
                    InventoryTable.owner_id == MaterialTable.id,
                ),
            )
        )

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    MaterialTable.sku.ilike(search),
                    MaterialTable.name.ilike(search),
                    MaterialTable.description.ilike(search),
                )
            )

        if filters.unit_type:
            statement = statement.where(
                MaterialTable.unit_type == filters.unit_type
            )

        if filters.availability_status:
            if filters.availability_status == AvailabilityStatus.OUT_OF_STOCK:
                statement = statement.where(
                    InventoryTable.quantity == 0
                )

            elif filters.availability_status == AvailabilityStatus.LOW_STOCK:
                statement = statement.where(
                    InventoryTable.quantity > 0,
                    InventoryTable.quantity < InventoryTable.minimum_quantity
                )

            elif filters.availability_status == AvailabilityStatus.AVAILABLE:
                statement = statement.where(
                    InventoryTable.quantity >= InventoryTable.minimum_quantity
                )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def save(
        self,
        material: MaterialTable,
    ) -> MaterialTable:
        self.session.add(material)

        await self.session.commit()
        await self.session.refresh(material)

        return material

    async def get_by_id(
        self,
        material_id: UUID,
    ) -> MaterialTable | None:
        statement = select(MaterialTable).where(
            MaterialTable.id == material_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get(
        self,
        filters: MaterialFilterSchema,
        offset: int = 0,
        limit: int = 20,
    ):

        statement = (
            select(
                MaterialTable,
                col(InventoryTable.quantity).label("current_stock"),
                col(InventoryTable.minimum_quantity).label("minimum_stock")
            )
            .join(
                InventoryTable,
                and_(
                    InventoryTable.owner_type == InventoryOwnerType.MATERIAL,
                    InventoryTable.owner_id == MaterialTable.id,
                ),
            )
        )

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    MaterialTable.sku.ilike(search),
                    MaterialTable.name.ilike(search),
                    MaterialTable.description.ilike(search),
                )
            )

        if filters.unit_type:
            statement = statement.where(
                MaterialTable.unit_type == filters.unit_type
            )


        if filters.availability_status:

            if filters.availability_status == AvailabilityStatus.OUT_OF_STOCK:
                statement = statement.where(
                    InventoryTable.quantity == 0
                )

            elif filters.availability_status == AvailabilityStatus.LOW_STOCK:
                statement = statement.where(
                    InventoryTable.quantity > 0,
                    InventoryTable.quantity < InventoryTable.minimum_quantity
                )

            elif filters.availability_status == AvailabilityStatus.AVAILABLE:
                statement = statement.where(
                    InventoryTable.quantity >= InventoryTable.minimum_quantity
                )

        statement = statement.offset(offset).limit(limit)

        result = await self.session.execute(statement)

        return result.all()

    async def delete_by_id(
        self,
        material_id: UUID,
    ) -> bool:
        statement = delete(MaterialTable).where(
            MaterialTable.id == material_id
        )

        result = await self.session.execute(statement)

        return result.rowcount > 0