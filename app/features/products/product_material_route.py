from uuid import UUID

from fastapi import APIRouter, Body, Depends, status

from app.features.products.dependencies.service import (
    get_product_material_service,
)
from app.features.products.schemas.product_material import (
    MaterialProductResponse,
    ProductMaterialResponse,
    ReplaceProductMaterialItemSchema,
)
from app.features.products.services.product_material_service import (
    ProductMaterialService
)

product_material_router = APIRouter(
    tags=["Product Materials"],
)


@product_material_router.get(
    "/products/{product_id}/materials",
    response_model=list[ProductMaterialResponse],
)
async def get_product_materials(
    product_id: UUID,
    service: ProductMaterialService = Depends(
        get_product_material_service,
    ),
):

    return await service.get_product_materials(
        product_id,
    )


@product_material_router.put(
    "/products/{product_id}/materials",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def replace_product_materials(
    product_id: UUID,
    data: list[ReplaceProductMaterialItemSchema] = Body(...),
    service: ProductMaterialService = Depends(
        get_product_material_service,
    ),
):

    return await service.replace_product_materials(
        product_id,
        data,
    )


@product_material_router.get(
    "/materials/{material_id}/products",
    response_model=list[MaterialProductResponse],
)
async def get_material_products(
    material_id: UUID,
    service: ProductMaterialService = Depends(
        get_product_material_service,
    ),
):

    return await service.get_material_products(
        material_id,
    )