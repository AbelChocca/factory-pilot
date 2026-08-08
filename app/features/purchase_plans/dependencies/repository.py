from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.features.purchase_plans.repository import (
    PurchasePlanRepository,
)


def get_purchase_plan_repository(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> PurchasePlanRepository:
    return PurchasePlanRepository(
        session=session,
    )