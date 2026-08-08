from uuid import UUID

from app.features.products.models.product_material import ProductMaterialTable
from app.features.products.repositories.product_material_repository import (
    ProductMaterialRepository,
)
from app.features.products.schemas.product_material import (
    MaterialProductResponse,
    ProductMaterialResponse,
    ReplaceProductMaterialItemSchema,
)


class ProductMaterialService:
    def __init__(
        self,
        repository: ProductMaterialRepository,
    ):
        self.repository = repository

    async def get_product_materials(
        self,
        product_id: UUID,
    ) -> list[ProductMaterialResponse]:

        return await self.repository.get_by_product_id(
            product_id
        )

    async def get_material_products(
        self,
        material_id: UUID,
    ) -> list[MaterialProductResponse]:

        return await self.repository.get_by_material_id(
            material_id
        )

    async def replace_product_materials(
        self,
        product_id: UUID,
        schema: list[ReplaceProductMaterialItemSchema],
    ) -> None:

        material_ids = [
            item.material_id
            for item in schema
        ]

        if len(material_ids) != len(set(material_ids)):
            raise ValueError(
                "Duplicate materials are not allowed."
            )

        await self.repository.delete_by_product_id(
            product_id
        )

        relations = [
            ProductMaterialTable(
                product_id=product_id,
                material_id=item.material_id,
                quantity=item.quantity,
            )
            for item in schema
        ]

        await self.repository.save_all(
            relations
        )