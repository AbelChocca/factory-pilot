from uuid import UUID

from sqlalchemy import delete, func, or_, select, and_
from sqlmodel import col
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.models.product import ProductTable
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import AvailabilityStatus, InventoryOwnerType
from app.features.products.schemas.product import ProductFilterSchema


class ProductRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def save(
        self,
        product: ProductTable,
    ) -> ProductTable:
        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def get_by_id(
        self,
        product_id: UUID,
    ) -> ProductTable | None:
        statement = select(ProductTable).where(
            ProductTable.id == product_id
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_sku(
        self,
        sku: str,
    ) -> ProductTable | None:
        statement = select(ProductTable).where(
            ProductTable.sku == sku
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get(
        self,
        filters: ProductFilterSchema,
        offset: int = 0,
        limit: int = 20,
    ):
        statement = (
            select(
                ProductTable,
                col(InventoryTable.quantity).label("current_stock"),
                col(InventoryTable.minimum_quantity).label("minimum_stock"),
            )
            .join(
                InventoryTable,
                and_(
                    InventoryTable.owner_type == InventoryOwnerType.PRODUCT,
                    InventoryTable.owner_id == ProductTable.id,
                ),
            )
        )

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    ProductTable.sku.ilike(search),
                    ProductTable.name.ilike(search),
                    ProductTable.description.ilike(search),
                )
            )

        if filters.availability_status:

            if filters.availability_status == AvailabilityStatus.OUT_OF_STOCK:
                statement = statement.where(
                    InventoryTable.quantity == 0
                )

            elif filters.availability_status == AvailabilityStatus.LOW_STOCK:
                statement = statement.where(
                    InventoryTable.quantity > 0,
                    InventoryTable.quantity < InventoryTable.minimum_quantity,
                )

            elif filters.availability_status == AvailabilityStatus.AVAILABLE:
                statement = statement.where(
                    InventoryTable.quantity >= InventoryTable.minimum_quantity
                )

        statement = statement.offset(offset).limit(limit)

        result = await self.session.execute(statement)

        return result.all()

    async def count(
        self,
        filters: ProductFilterSchema,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ProductTable)
            .join(
                InventoryTable,
                and_(
                    InventoryTable.owner_type == InventoryOwnerType.PRODUCT,
                    InventoryTable.owner_id == ProductTable.id,
                ),
            )
        )

        if filters.query:
            search = f"%{filters.query}%"

            statement = statement.where(
                or_(
                    ProductTable.sku.ilike(search),
                    ProductTable.name.ilike(search),
                    ProductTable.description.ilike(search),
                )
            )

        if filters.availability_status:

            if filters.availability_status == AvailabilityStatus.OUT_OF_STOCK:
                statement = statement.where(
                    InventoryTable.quantity == 0
                )

            elif filters.availability_status == AvailabilityStatus.LOW_STOCK:
                statement = statement.where(
                    InventoryTable.quantity > 0,
                    InventoryTable.quantity < InventoryTable.minimum_quantity,
                )

            elif filters.availability_status == AvailabilityStatus.AVAILABLE:
                statement = statement.where(
                    InventoryTable.quantity >= InventoryTable.minimum_quantity
                )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def delete_by_id(
        self,
        product_id: UUID,
    ) -> bool:
        statement = delete(ProductTable).where(
            ProductTable.id == product_id
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0