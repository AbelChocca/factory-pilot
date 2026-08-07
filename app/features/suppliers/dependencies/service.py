from fastapi import Depends

from app.features.suppliers.dependencies.repository import (
    get_supplier_repository,
)
from app.features.suppliers.repositories.supplier_repository import SupplierRepository
from app.features.suppliers.services.supplier import SupplierService
from app.features.suppliers.services.supplier_material import (
    SupplierMaterialService,
)
from app.features.suppliers.dependencies.repository import (
    get_supplier_material_repository,
)
from app.features.suppliers.repositories.supplier_material_repository import (
    SupplierMaterialRepository,
)


def get_supplier_service(
    repository: SupplierRepository = Depends(
        get_supplier_repository,
    ),
) -> SupplierService:
    return SupplierService(
        supplier_repository=repository,
    )

def get_supplier_material_service(
    repository: SupplierMaterialRepository = Depends(
        get_supplier_material_repository,
    ),
) -> SupplierMaterialService:
    return SupplierMaterialService(
        repository=repository,
    )