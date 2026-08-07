from uuid import UUID

from app.features.suppliers.models.supplier import SupplierTable
from app.features.suppliers.repositories.supplier_repository import SupplierRepository
from app.features.suppliers.schemas.supplier import (
    CreateSupplierSchema,
    SupplierFilterSchema,
    SupplierResponseSchema,
)
from app.shared.enums import Status
from app.shared.pagination import PaginationHelper
from app.shared.schema import PaginatedResponseSchema


class SupplierService:
    def __init__(
        self,
        supplier_repository: SupplierRepository,
    ):
        self.supplier_repository = supplier_repository

    def to_response(
        self,
        supplier: SupplierTable,
    ) -> SupplierResponseSchema:
        return SupplierResponseSchema(
            id=supplier.id,
            name=supplier.name,
            email=supplier.email,
            phone=supplier.phone,
            lead_time_days=supplier.lead_time_days,
            status=supplier.status,
        )

    async def get_by_id(
        self,
        supplier_id: UUID,
    ) -> SupplierResponseSchema | None:

        supplier = await self.supplier_repository.get_by_id(supplier_id)

        if not supplier:
            return None

        return self.to_response(supplier)

    async def get(
        self,
        filters: SupplierFilterSchema,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponseSchema[SupplierResponseSchema]:

        offset = PaginationHelper.page_to_offset(
            page,
            limit,
        )

        total_items = await self.supplier_repository.count(filters)

        suppliers = await self.supplier_repository.get(
            filters,
            offset,
            limit,
        )

        suppliers = [
            self.to_response(supplier)
            for supplier in suppliers
        ]

        return PaginatedResponseSchema[SupplierResponseSchema](
            items=suppliers,
            total_items=total_items,
            total_pages=PaginationHelper.total_pages(
                total_items,
                limit,
            ),
            current_page=PaginationHelper.offset_to_page(
                offset,
                limit,
            ),
        )

    async def create(
        self,
        schema: CreateSupplierSchema,
    ) -> SupplierResponseSchema:

        supplier = SupplierTable(
            name=schema.name,
            email=schema.email,
            phone=schema.phone,
            lead_time_days=schema.lead_time_days,
            status=Status.ACTIVE,
        )

        supplier = await self.supplier_repository.save(supplier)

        return self.to_response(supplier)

    async def delete(
        self,
        supplier_id: UUID,
    ) -> bool:

        return await self.supplier_repository.delete_by_id(
            supplier_id
        )