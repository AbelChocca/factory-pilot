from fastapi import Depends
from app.features.materials.repository import MaterialRepository
from app.features.materials.service import MaterialService
from app.features.inventory.repositories.inventory_movement_repository import InventoryMovementRepository
from app.features.inventory.repositories.inventory_repository import InventoryRepository
from app.features.inventory.dependencies.repository import get_inventory_movement_repository, get_inventory_repository
from app.features.materials.dependencies.repository import get_material_repository



def get_material_service(
    repository: MaterialRepository = Depends(get_material_repository),
    inventory_movement: InventoryMovementRepository = Depends(get_inventory_movement_repository),
    inventory: InventoryRepository = Depends(get_inventory_repository)
) -> MaterialService:
    return MaterialService(
        material_repository=repository,
        inventory_movement_repository=inventory_movement,
        inventory_repository=inventory
    )
