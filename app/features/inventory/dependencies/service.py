
from fastapi import Depends

from app.features.inventory.repositories.inventory_repository import (
    InventoryRepository,
)

from app.features.inventory.repositories.inventory_movement_repository import (
    InventoryMovementRepository,
)

from app.features.inventory.services.inventory_movements_service import (
    InventoryMovementService,
)
from app.features.materials.dependencies.repository import get_material_repository
from app.features.materials.repository import MaterialRepository

from app.features.inventory.dependencies.repository import get_inventory_repository, get_inventory_movement_repository
from app.features.inventory.services.inventory_service import InventoryService


def get_inventory_movement_service(
    repository: InventoryMovementRepository = Depends(
        get_inventory_movement_repository,
    ),
    inventory_repository: InventoryRepository = Depends(
        get_inventory_repository
    ),
    material_repository: MaterialRepository = Depends(
        get_material_repository
    )
) -> InventoryMovementService:
    return InventoryMovementService(
        repository=repository,
        inventory_repository=inventory_repository,
        material_repository=material_repository
    )

def get_inventory_service(
    repository: InventoryRepository = Depends(
        get_inventory_repository,
    ),
) -> InventoryService:
    return InventoryService(
        inventory_repository=repository,
    )