from uuid import UUID

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body

from app.features.materials.dependencies.service import get_material_service
from app.features.materials.schema import (
    CreateMaterialSchema,
    MaterialFilterSchema,
    MaterialResponseSchema,
)
from app.features.materials.service import MaterialService
from app.shared.schema import PaginatedResponseSchema


material_router = APIRouter(
    prefix="/materials",
    tags=["Materials"],
)


@material_router.post(
    "/",
    response_model=MaterialResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_material(
    data: Annotated[CreateMaterialSchema, Body()],
    service: MaterialService = Depends(get_material_service),
):

    material = await service.create(data)

    return material


@material_router.get(
    "/",
    response_model=PaginatedResponseSchema[MaterialResponseSchema],
)
async def get_materials(
    filters: Annotated[MaterialFilterSchema, Depends()],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: MaterialService = Depends(get_material_service),
):

    return await service.get(filters, page, limit)


@material_router.get(
    "/{material_id}",
    response_model=MaterialResponseSchema,
)
async def get_material_by_id(
    material_id: UUID,
    service: MaterialService = Depends(get_material_service),
):
    material = await service.get_by_id(material_id)

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )

    return material


@material_router.delete(
    "/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_material(
    material_id: UUID,
    service: MaterialService = Depends(get_material_service),
):
    deleted = await service.delete(material_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )