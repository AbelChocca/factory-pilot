from uuid import UUID
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
    Query
)

from app.features.purchase_plans.dependencies.service import (
    get_purchase_plan_service,
)
from app.features.purchase_plans.schema import (
    CreatePurchasePlanSchema,
    UpdatePurchasePlanSchema,
    PurchasePlanResponseSchema,
    PurchasePlanItem
)
from app.shared.schema import PaginatedResponseSchema
from app.features.purchase_plans.service import (
    PurchasePlanService,
)


purchase_plan_router = APIRouter(
    prefix="/purchase-plans",
    tags=["Purchase Plans"],
)


@purchase_plan_router.get(
    "/current",
)
async def get_current_purchase_plan(
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):
    purchase_plan = await service.get_current()

    if not purchase_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current purchase plan not found",
        )

    return purchase_plan


@purchase_plan_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase_plan(
    data: Annotated[
        CreatePurchasePlanSchema,
        Body(),
    ],
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):
    try:
        await service.create(data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@purchase_plan_router.get(
    "/{purchase_plan_id}",
)
async def get_purchase_plan_by_id(
    purchase_plan_id: UUID,
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):
    purchase_plan = await service.get_by_id(
        purchase_plan_id,
    )

    if not purchase_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase plan not found",
        )

    return purchase_plan


@purchase_plan_router.get(
    "/{purchase_plan_id}/items",
    response_model=list[PurchasePlanItem]
)
async def get_purchase_plan_items(
    purchase_plan_id: UUID,
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
) -> list[PurchasePlanItem]:
    purchase_plan = await service.get_by_id(
        purchase_plan_id,
    )

    if not purchase_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase plan not found",
        )

    return await service.get_items(
        purchase_plan_id,
    )

@purchase_plan_router.get(
    "/",
    response_model=PaginatedResponseSchema[
        PurchasePlanResponseSchema
    ],
)
async def get_purchase_plans(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):
    return await service.get_all(
        page=page,
        limit=limit,
        search=search
    )

@purchase_plan_router.put(
    "/{purchase_plan_id}",
)
async def update_purchase_plan(
    purchase_plan_id: UUID,
    data: Annotated[
        UpdatePurchasePlanSchema,
        Body(),
    ],
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):

    try:
        purchase_plan = await service.update(purchase_plan_id, data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if not purchase_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase plan not found",
        )

    return None


@purchase_plan_router.post(
    "/{purchase_plan_id}/approve",
)
async def approve_purchase_plan(
    purchase_plan_id: UUID,
    service: PurchasePlanService = Depends(
        get_purchase_plan_service,
    ),
):
    try:
        purchase_plan = await service.approve(
            purchase_plan_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    if not purchase_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase plan not found",
        )

    return None