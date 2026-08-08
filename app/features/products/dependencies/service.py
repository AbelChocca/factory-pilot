from app.features.products.dependencies.repository import get_product_repository
from app.features.inventory.dependencies.repository import get_inventory_repository, get_inventory_movement_repository
from app.features.inventory.repositories.inventory_repository import InventoryRepository
from app.features.inventory.repositories.inventory_movement_repository import InventoryMovementRepository
from app.features.products.services.product_service import ProductService
from app.features.products.repositories.product_repository import ProductRepository
from app.features.products.dependencies.repository import (
    get_product_material_repository,
)
from app.features.products.repositories.product_material_repository import (
    ProductMaterialRepository,
)
from app.features.products.services.product_material_service import (
    ProductMaterialService,
)

from fastapi import Depends

def get_product_service(
    product_repository: ProductRepository = Depends(
        get_product_repository,
    ),
    inventory_repository: InventoryRepository = Depends(
        get_inventory_repository,
    ),
    inventory_movement_repository: InventoryMovementRepository = Depends(
        get_inventory_movement_repository,
    ),
) -> ProductService:
    return ProductService(
        product_repository=product_repository,
        inventory_repository=inventory_repository,
        inventory_movement_repository=inventory_movement_repository,
    )

def get_product_material_service(
    repository: ProductMaterialRepository = Depends(
        get_product_material_repository,
    ),
) -> ProductMaterialService:

    return ProductMaterialService(
        repository=repository,
    )