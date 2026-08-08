from typing import Annotated

from fastapi import APIRouter, Depends, Depends, Query, status, Body

from app.features.inventory.dependencies.service import (
    get_inventory_movement_service,
)
from app.features.inventory.schema import (
    InventoryMovementFilterSchema,
    InventoryMovementResponseSchema,
    CreateInventoryMovementSchema
)
from app.features.inventory.services.inventory_movements_service import (
    InventoryMovementService,
)
from app.shared.schema import PaginatedResponseSchema

inventory_movement_router = APIRouter(
    prefix="/inventory-movements",
    tags=["Inventory Movements"],
)


@inventory_movement_router.get(
    "/",
    response_model=PaginatedResponseSchema[
        InventoryMovementResponseSchema
    ],
)
async def get_inventory_movements(
    filters: Annotated[InventoryMovementFilterSchema, Depends()],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: InventoryMovementService = Depends(
        get_inventory_movement_service,
    ),
):
    return await service.get(
        filters=filters,
        page=page,
        limit=limit,
    )

@inventory_movement_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_inventory_movement(
    data:  Annotated[CreateInventoryMovementSchema, Body()],
    service: InventoryMovementService = Depends(
        get_inventory_movement_service,
    ),
):
    await service.create(data)