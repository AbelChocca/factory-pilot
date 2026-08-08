from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    status,
)

from app.features.products.dependencies.service import get_product_service
from app.features.products.schemas.product import (
    CreateProductSchema,
    ProductFilterSchema,
    ProductResponseSchema,
)
from app.features.products.services.product_service import ProductService
from app.shared.schema import PaginatedResponseSchema

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@product_router.post(
    "/",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: Annotated[CreateProductSchema, Form()],
    service: ProductService = Depends(get_product_service),
):
    return await service.create(data)

@product_router.get(
    "/",
    response_model=PaginatedResponseSchema[ProductResponseSchema],
)
async def get_products(
    filters: Annotated[ProductFilterSchema, Depends()],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: ProductService = Depends(get_product_service),
):
    return await service.get(
        filters=filters,
        page=page,
        limit=limit,
    )

@product_router.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
)
async def get_product_by_id(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    product = await service.get_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product

@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    deleted = await service.delete(product_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )