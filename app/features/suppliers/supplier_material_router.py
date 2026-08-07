from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

from app.features.suppliers.dependencies.service import (
    get_supplier_material_service,
)
from app.features.suppliers.schemas.supplier_material import (
    MaterialSupplierResponse,
    ReplaceMaterialSupplierItemSchema,
    SupplierMaterialResponse,
)
from app.features.suppliers.services.supplier_material import (
    SupplierMaterialService,
)

supplier_material_router = APIRouter(
    tags=["Supplier Materials"],
)


@supplier_material_router.get(
    "/materials/{material_id}/suppliers",
    response_model=list[MaterialSupplierResponse],
)
async def get_material_suppliers(
    material_id: UUID,
    service: SupplierMaterialService = Depends(
        get_supplier_material_service,
    ),
):

    return await service.get_material_suppliers(
        material_id
    )


@supplier_material_router.put(
    "/materials/{material_id}/suppliers",
    status_code=status.HTTP_204_NO_CONTENT
)
async def replace_material_suppliers(
    material_id: UUID,
    data: list[ReplaceMaterialSupplierItemSchema] = Body(...),
    service: SupplierMaterialService = Depends(
        get_supplier_material_service,
    ),
):

    return await service.replace_material_suppliers(
        material_id,
        data,
    )


@supplier_material_router.get(
    "/materials/{material_id}/preferred-supplier",
    response_model=MaterialSupplierResponse | None,
)
async def get_preferred_supplier(
    material_id: UUID,
    service: SupplierMaterialService = Depends(
        get_supplier_material_service,
    ),
):

    return await service.get_preferred_supplier(
        material_id
    )


@supplier_material_router.get(
    "/suppliers/{supplier_id}/materials",
    response_model=list[SupplierMaterialResponse],
)
async def get_supplier_materials(
    supplier_id: UUID,
    service: SupplierMaterialService = Depends(
        get_supplier_material_service,
    ),
):

    return await service.get_supplier_materials(
        supplier_id
    )