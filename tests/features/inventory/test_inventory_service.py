from decimal import Decimal

import pytest

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType
from app.features.materials.model import MaterialTable
from app.features.materials.types import MaterialType
from app.shared.enums import Status
from app.shared.types import UnitType


@pytest.mark.asyncio
async def test_get_low_stock_materials(
    db_session,
    inventory_service,
):
    low_stock_material = MaterialTable(
        sku="MDF-18",
        name="MDF Board 18 mm",
        description="MDF board 18 mm",
        material_type=MaterialType.RAW_MATERIAL,
        unit_type=UnitType.SQUARE_METER,
        status=Status.ACTIVE,
    )

    normal_stock_material = MaterialTable(
        sku="PLY-15",
        name="Plywood 15 mm",
        description="Plywood board 15 mm",
        material_type=MaterialType.RAW_MATERIAL,
        unit_type=UnitType.SQUARE_METER,
        status=Status.ACTIVE,
    )

    db_session.add(low_stock_material)
    db_session.add(normal_stock_material)

    await db_session.commit()
    await db_session.refresh(low_stock_material)
    await db_session.refresh(normal_stock_material)

    low_stock_inventory = InventoryTable(
        owner_type=InventoryOwnerType.MATERIAL,
        owner_id=low_stock_material.id,
        quantity=Decimal("42"),
        minimum_quantity=Decimal("100"),
    )

    normal_stock_inventory = InventoryTable(
        owner_type=InventoryOwnerType.MATERIAL,
        owner_id=normal_stock_material.id,
        quantity=Decimal("200"),
        minimum_quantity=Decimal("100"),
    )

    db_session.add(low_stock_inventory)
    db_session.add(normal_stock_inventory)

    await db_session.commit()

    result = await inventory_service.get_low_stock_materials()

    assert len(result) == 1

    material = result[0]

    assert material.material_id == low_stock_material.id
    assert material.sku == "MDF-18"
    assert material.name == "MDF Board 18 mm"
    assert material.quantity == Decimal("42")
    assert material.minimum_quantity == Decimal("100")
    assert material.unit_type == UnitType.SQUARE_METER.value