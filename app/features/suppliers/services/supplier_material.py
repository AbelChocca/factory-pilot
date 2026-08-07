from uuid import UUID

from app.features.suppliers.models.supplier_material import SupplierMaterialTable
from app.features.suppliers.repositories.supplier_material_repository import (
    SupplierMaterialRepository,
)
from app.features.suppliers.schemas.supplier_material import (
    MaterialSupplierResponse,
    ReplaceMaterialSupplierItemSchema,
    SupplierMaterialResponse,
    MaterialSupplierDetailResponse
)

class SupplierMaterialService:
    def __init__(
        self,
        repository: SupplierMaterialRepository,
    ):
        self.repository = repository

    async def get_material_suppliers(
        self,
        material_ids: list[UUID],
    ) -> list[MaterialSupplierDetailResponse]:

        return await self.repository.get_by_material_ids(
            material_ids
        )

    async def get_supplier_materials(
        self,
        supplier_id: UUID,
    ) -> list[SupplierMaterialResponse]:

        return await self.repository.get_by_supplier_id(
            supplier_id
        )

    async def get_preferred_supplier(
        self,
        material_id: UUID,
    ) -> MaterialSupplierResponse | None:

        return await self.repository.get_preferred_supplier(
            material_id
        )

    async def replace_material_suppliers(
        self,
        material_id: UUID,
        schema: list[ReplaceMaterialSupplierItemSchema],
    ) -> None:

        preferred_count = sum(
            item.preferred
            for item in schema
        )

        if preferred_count > 1:
            raise ValueError(
                "Only one preferred supplier is allowed."
            )

        await self.repository.delete_by_material_id(
            material_id
        )

        relations = [
            SupplierMaterialTable(
                supplier_id=item.supplier_id,
                material_id=material_id,
                supplier_sku=item.supplier_sku,
                unit_price=item.unit_price,
                preferred=item.preferred,
            )
            for item in schema
        ]

        await self.repository.save_all(
            relations
        )