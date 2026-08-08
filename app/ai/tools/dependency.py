from fastapi import Depends

from app.ai.tools.ai_tool import AITool
from app.ai.tools.inventory.dependencies import (
    get_low_stock_materials_tool,
)
from app.ai.tools.inventory.get_low_stock_materials import (
    GetLowStockMaterialsTool,
)
from app.ai.tools.knowledge.dependencies import (
    get_search_knowledge_tool,
)
from app.ai.tools.knowledge.search_knowledge import (
    SearchKnowledgeTool,
)
from app.ai.tools.purchase_plan.approve_purchase_plan import (
    ApprovePurchasePlanTool,
)
from app.ai.tools.purchase_plan.dependencies import (
    get_approve_purchase_plan_tool,
    get_generate_purchase_plan_tool,
    get_update_purchase_plan_tool,
)
from app.ai.tools.purchase_plan.generate_purchase_plan import (
    GeneratePurchasePlanTool,
)
from app.ai.tools.purchase_plan.update_purchase_plan import (
    UpdatePurchasePlanTool,
)
from app.ai.tools.suppliers.dependencies import (
    get_materials_suppliers_tool,
)
from app.ai.tools.suppliers.get_material_suppliers_tool import (
    GetMaterialSuppliersTool,
)
from app.ai.tools.analyzer.analyze_production_risk import (
    AnalyzeProductionRiskTool
)
from app.ai.tools.analyzer.dependencies import (
    get_analyze_production_risk_tool,
    get_analyze_material_impact_tool
)
from app.ai.tools.materials.search_materials import SearchMaterialsTool
from app.ai.tools.materials.dependencies import get_search_materials_tool
from app.ai.tools.analyzer.analyze_material_impact import AnalyzeMaterialImpactTool
from app.ai.tools.tool_registry import ToolRegistry


def get_tool_registry(
    low_stock_tool: GetLowStockMaterialsTool = Depends(
        get_low_stock_materials_tool,
    ),
    search_knowledge_tool: SearchKnowledgeTool = Depends(
        get_search_knowledge_tool,
    ),
    materials_suppliers_tool: GetMaterialSuppliersTool = Depends(
        get_materials_suppliers_tool,
    ),
    generate_purchase_plan_tool: GeneratePurchasePlanTool = Depends(
        get_generate_purchase_plan_tool,
    ),
    update_purchase_plan_tool: UpdatePurchasePlanTool = Depends(
        get_update_purchase_plan_tool,
    ),
    approve_purchase_plan_tool: ApprovePurchasePlanTool = Depends(
        get_approve_purchase_plan_tool,
    ),
    analyze_production_risk_tool: AnalyzeProductionRiskTool = Depends(
        get_analyze_production_risk_tool,
    ),
    analyze_material_impact_tool: AnalyzeMaterialImpactTool = Depends(
        get_analyze_material_impact_tool
    ),
    search_materials_tool: SearchMaterialsTool = Depends(
        get_search_materials_tool
    )
) -> ToolRegistry:

    tools: list[AITool] = [
        low_stock_tool,
        search_knowledge_tool,
        materials_suppliers_tool,
        generate_purchase_plan_tool,
        update_purchase_plan_tool,
        approve_purchase_plan_tool,
        analyze_production_risk_tool,
        analyze_material_impact_tool,
        search_materials_tool,
    ]

    return ToolRegistry(
        tools=tools,
    )