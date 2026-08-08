from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session

from app.features.inventory.repositories.inventory_repository import (
    InventoryRepository,
)

from app.features.inventory.repositories.inventory_movement_repository import (
    InventoryMovementRepository,
)
def get_inventory_repository(
    session: AsyncSession = Depends(get_db_session),
) -> InventoryRepository:
    return InventoryRepository(
        session=session,
    )


def get_inventory_movement_repository(
    session: AsyncSession = Depends(get_db_session),
) -> InventoryMovementRepository:
    return InventoryMovementRepository(
        session=session,
    )