from uuid import UUID

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.materials.model import MaterialTable
from app.features.products.models.product import ProductTable
from app.features.products.models.product_material import ProductMaterialTable
from app.features.products.schemas.product_material import (
    ProductMaterialResponse,
    MaterialProductResponse,
)


class ProductMaterialRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def count(self) -> int:
        statement = select(func.count()).select_from(
            ProductMaterialTable
        )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def save(
        self,
        product_material: ProductMaterialTable,
    ) -> ProductMaterialTable:

        self.session.add(product_material)

        await self.session.commit()
        await self.session.refresh(product_material)

        return product_material

    async def save_all(
        self,
        product_materials: list[ProductMaterialTable],
    ) -> None:

        self.session.add_all(product_materials)

        await self.session.commit()

    async def get_by_product_id(
        self,
        product_id: UUID,
    ) -> list[ProductMaterialResponse]:

        statement = (
            select(
                ProductMaterialTable,
                MaterialTable,
            )
            .join(
                MaterialTable,
                MaterialTable.id == ProductMaterialTable.material_id,
            )
            .where(
                ProductMaterialTable.product_id == product_id
            )
            .order_by(
                MaterialTable.name,
            )
        )

        result = await self.session.execute(statement)

        return [
            ProductMaterialResponse(
                material_id=material.id,
                material_name=material.name,
                material_sku=material.sku,
                material_type=material.material_type,
                unit_type=material.unit_type,
                quantity=relation.quantity,
            )
            for relation, material in result.all()
        ]

    async def get_by_material_id(
        self,
        material_id: UUID,
    ) -> list[MaterialProductResponse]:

        statement = (
            select(
                ProductMaterialTable,
                ProductTable,
            )
            .join(
                ProductTable,
                ProductTable.id == ProductMaterialTable.product_id,
            )
            .where(
                ProductMaterialTable.material_id == material_id
            )
            .order_by(
                ProductTable.name,
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialProductResponse(
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                quantity=relation.quantity,
            )
            for relation, product in result.all()
        ]

    async def get_by_product_and_material(
        self,
        product_id: UUID,
        material_id: UUID,
    ) -> ProductMaterialTable | None:

        statement = (
            select(ProductMaterialTable)
            .where(
                and_(
                    ProductMaterialTable.product_id == product_id,
                    ProductMaterialTable.material_id == material_id,
                )
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def delete(
        self,
        product_id: UUID,
        material_id: UUID,
    ) -> bool:

        statement = (
            delete(ProductMaterialTable)
            .where(
                and_(
                    ProductMaterialTable.product_id == product_id,
                    ProductMaterialTable.material_id == material_id,
                )
            )
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    async def delete_by_product_id(
        self,
        product_id: UUID,
    ) -> None:

        statement = (
            delete(ProductMaterialTable)
            .where(
                ProductMaterialTable.product_id == product_id
            )
        )

        await self.session.execute(statement)

        await self.session.commit()

    async def delete_by_material_id(
        self,
        material_id: UUID,
    ) -> None:

        statement = (
            delete(ProductMaterialTable)
            .where(
                ProductMaterialTable.material_id == material_id
            )
        )

        await self.session.execute(statement)

        await self.session.commit()