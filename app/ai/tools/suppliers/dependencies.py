from app.ai.tools.suppliers.get_material_suppliers_tool import GetMaterialSuppliersTool
from app.features.suppliers.dependencies.service import get_supplier_material_service
from app.features.suppliers.services.supplier_material import SupplierMaterialService

from fastapi import Depends

def get_materials_suppliers_tool(
    supplier_material_service: SupplierMaterialService = Depends(get_supplier_material_service)
) -> GetMaterialSuppliersTool:
    return GetMaterialSuppliersTool(
        supplier_material_service=supplier_material_service
    )