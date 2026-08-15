from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.features.inventory.types import InventoryOwnerType
from app.features.materials.model import MaterialTable
from app.features.products.models.product import ProductTable
from app.features.inventory.schema import InventoryOwnerInfo
from app.shared.types import UnitType

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

    async def get_for_trend_analysis(
        self,
        owner_type: InventoryOwnerType | None = None,
        owner_id: UUID | None = None,
    ) -> list[
        tuple[
            InventoryTable,
            InventoryOwnerInfo,
        ]
    ]:

        statement = select(InventoryTable)

        if owner_type is not None:
            statement = statement.where(
                InventoryTable.owner_type == owner_type,
            )

        if owner_id is not None:
            statement = statement.where(
                InventoryTable.owner_id == owner_id,
            )

        result = await self.session.execute(statement)

        inventories = list(result.scalars().all())

        if not inventories:
            return []

        material_ids = [
            inventory.owner_id
            for inventory in inventories
            if inventory.owner_type == InventoryOwnerType.MATERIAL
        ]

        product_ids = [
            inventory.owner_id
            for inventory in inventories
            if inventory.owner_type == InventoryOwnerType.PRODUCT
        ]

        materials = {}

        if material_ids:
            material_statement = select(MaterialTable).where(
                MaterialTable.id.in_(material_ids),
            )

            material_result = await self.session.execute(
                material_statement,
            )

            materials = {
                material.id: material
                for material in material_result.scalars().all()
            }

        products = {}

        if product_ids:
            product_statement = select(ProductTable).where(
                ProductTable.id.in_(product_ids),
            )

            product_result = await self.session.execute(
                product_statement,
            )

            products = {
                product.id: product
                for product in product_result.scalars().all()
            }

        rows = []

        for inventory in inventories:

            if inventory.owner_type == InventoryOwnerType.MATERIAL:
                material = materials.get(inventory.owner_id)

                if material is None:
                    continue

                owner_info = InventoryOwnerInfo(
                    owner_name=material.name,
                    owner_code=material.sku,
                    unit_type=material.unit_type,
                )

            else:
                product = products.get(inventory.owner_id)

                if product is None:
                    continue

                owner_info = InventoryOwnerInfo(
                    owner_name=product.name,
                    owner_code=product.sku,
                    unit_type=UnitType.UNIT,
                )

            rows.append(
                (
                    inventory,
                    owner_info,
                )
            )

        return rows

    async def get_movements_for_trend_analysis(
        self,
        inventory_ids: list[UUID],
        created_from: datetime,
        created_to: datetime,
    ) -> list[InventoryMovementTable]:
        if not inventory_ids:
            return []

        statement = (
            select(InventoryMovementTable)
            .where(
                InventoryMovementTable.inventory_id.in_(inventory_ids),
                InventoryMovementTable.created_at >= created_from,
                InventoryMovementTable.created_at <= created_to,
            )
            .order_by(
                InventoryMovementTable.created_at.asc(),
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())