from uuid import UUID

from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.features.suppliers.dependencies.service import (
    get_supplier_service,
)
from app.features.suppliers.schemas.supplier import (
    CreateSupplierSchema,
    SupplierFilterSchema,
    SupplierResponseSchema,
)
from app.features.suppliers.services.supplier import SupplierService
from app.shared.schema import PaginatedResponseSchema


supplier_router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


@supplier_router.post(
    "/",
    response_model=SupplierResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    data: Annotated[CreateSupplierSchema, Body()],
    service: SupplierService = Depends(get_supplier_service),
):
    supplier = await service.create(data)

    return supplier


@supplier_router.get(
    "/",
    response_model=PaginatedResponseSchema[SupplierResponseSchema],
)
async def get_suppliers(
    filters: Annotated[SupplierFilterSchema, Depends()],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: SupplierService = Depends(get_supplier_service),
):
    return await service.get(
        filters,
        page,
        limit,
    )


@supplier_router.get(
    "/{supplier_id}",
    response_model=SupplierResponseSchema,
)
async def get_supplier_by_id(
    supplier_id: UUID,
    service: SupplierService = Depends(get_supplier_service),
):
    supplier = await service.get_by_id(supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    return supplier


@supplier_router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_supplier(
    supplier_id: UUID,
    service: SupplierService = Depends(get_supplier_service),
):
    deleted = await service.delete(supplier_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )