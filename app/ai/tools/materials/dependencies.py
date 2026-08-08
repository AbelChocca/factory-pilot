from fastapi import Depends

from app.ai.tools.materials.search_materials import SearchMaterialsTool
from app.features.materials.service import MaterialService
from app.features.materials.dependencies.service import (
    get_material_service,
)


def get_search_materials_tool(
    material_service: MaterialService = Depends(
        get_material_service,
    ),
) -> SearchMaterialsTool:

    return SearchMaterialsTool(
        material_service=material_service,
    )