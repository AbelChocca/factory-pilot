from fastapi import Depends

from app.features.purchase_plans.dependencies.repository import (
    get_purchase_plan_repository,
)
from app.features.purchase_plans.repository import (
    PurchasePlanRepository,
)
from app.features.purchase_plans.service import (
    PurchasePlanService,
)
from app.features.suppliers.dependencies.repository import (
    get_supplier_material_repository,
)
from app.features.suppliers.repositories.supplier_material_repository import (
    SupplierMaterialRepository,
)


def get_purchase_plan_service(
    purchase_plan_repository: PurchasePlanRepository = Depends(
        get_purchase_plan_repository,
    ),
    supplier_material_repository: SupplierMaterialRepository = Depends(
        get_supplier_material_repository,
    ),
) -> PurchasePlanService:
    return PurchasePlanService(
        purchase_plan_repository=purchase_plan_repository,
        supplier_material_repository=supplier_material_repository,
    )