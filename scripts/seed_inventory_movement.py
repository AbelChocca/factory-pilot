from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import async_session_factory
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.models.inventory_movement import InventoryMovementTable
from app.features.materials.model import MaterialTable
from app.features.products.models.product import ProductTable
from app.features.inventory.types import InventoryMovementType, InventoryOwnerType
from app.shared.types import UnitType


TOTAL_MOVEMENTS = 300

random.seed(42)


MATERIAL_IN_REASONS = [
    "Material received from supplier",
    "Purchase order received",
    "Material replenishment",
    "Supplier delivery received",
]

MATERIAL_OUT_REASONS = [
    "Material consumed in production",
    "Production order consumption",
    "Material issued to production",
    "Manufacturing consumption",
]

MATERIAL_ADJUSTMENT_REASONS = [
    "Inventory count adjustment",
    "Cycle count correction",
    "Physical inventory reconciliation",
]

PRODUCT_IN_REASONS = [
    "Production completed",
    "Manufacturing order completed",
    "Finished product received",
]

PRODUCT_OUT_REASONS = [
    "Customer order dispatched",
    "Finished product shipment",
    "Sales order fulfillment",
]

PRODUCT_ADJUSTMENT_REASONS = [
    "Finished goods inventory adjustment",
    "Physical inventory reconciliation",
    "Stock count correction",
]


def get_reason(
    owner_type: InventoryOwnerType,
    movement_type: InventoryMovementType,
) -> str:
    if owner_type == InventoryOwnerType.MATERIAL:
        if movement_type == InventoryMovementType.IN:
            return random.choice(MATERIAL_IN_REASONS)

        if movement_type == InventoryMovementType.OUT:
            return random.choice(MATERIAL_OUT_REASONS)

        return random.choice(MATERIAL_ADJUSTMENT_REASONS)

    if movement_type == InventoryMovementType.IN:
        return random.choice(PRODUCT_IN_REASONS)

    if movement_type == InventoryMovementType.OUT:
        return random.choice(PRODUCT_OUT_REASONS)

    return random.choice(PRODUCT_ADJUSTMENT_REASONS)


def random_movement_type(
    quantity: Decimal,
    minimum_quantity: Decimal,
) -> InventoryMovementType:
    """
    Bias the movement according to current stock.

    Low stock -> more IN movements.
    Healthy stock -> balanced movements.
    """

    if quantity <= minimum_quantity:
        return random.choices(
            [
                InventoryMovementType.IN,
                InventoryMovementType.OUT,
                InventoryMovementType.ADJUSTMENT,
            ],
            weights=[65, 20, 15],
        )[0]

    return random.choices(
        [
            InventoryMovementType.IN,
            InventoryMovementType.OUT,
            InventoryMovementType.ADJUSTMENT,
        ],
        weights=[40, 45, 15],
    )[0]


def generate_quantity(
    movement_type: InventoryMovementType,
    current_quantity: Decimal,
    unit_type: UnitType,
) -> Decimal:
    if movement_type == InventoryMovementType.ADJUSTMENT:
        raise ValueError(
            "ADJUSTMENT quantity must be generated separately."
        )

    if movement_type == InventoryMovementType.OUT:
        if current_quantity <= 0:
            return Decimal("0")

        if unit_type == UnitType.UNIT:
            max_quantity = max(
                1,
                min(
                    int(current_quantity),
                    20,
                ),
            )

            return Decimal(
                random.randint(1, max_quantity)
            )

        max_quantity = min(
            current_quantity,
            Decimal("25"),
        )

        return Decimal(
            str(
                round(
                    random.uniform(
                        1,
                        float(max_quantity),
                    ),
                    2,
                )
            )
        )

    # IN
    if unit_type == UnitType.UNIT:
        return Decimal(
            random.randint(1, 20)
        )

    return Decimal(
        str(
            round(
                random.uniform(1, 25),
                2,
            )
        )
    )


def generate_adjustment_quantity(
    current_quantity: Decimal,
    minimum_quantity: Decimal,
    unit_type: UnitType,
) -> Decimal:
    base = max(
        current_quantity,
        minimum_quantity,
        Decimal("1"),
    )

    multiplier = Decimal(
        str(
            round(
                random.uniform(0.5, 1.8),
                2,
            )
        )
    )

    new_quantity = base * multiplier

    if unit_type == UnitType.UNIT:
        return Decimal(int(new_quantity))

    return new_quantity.quantize(Decimal("0.01"))


def random_created_at(
    start: datetime,
    end: datetime,
) -> datetime:
    total_seconds = int((end - start).total_seconds())

    return start + timedelta(
        seconds=random.randint(0, total_seconds),
    )


async def get_owner_data(
    session: AsyncSession,
    inventory: InventoryTable,
) -> tuple[str, str, UnitType]:
    if inventory.owner_type == InventoryOwnerType.MATERIAL:
        material = await session.get(
            MaterialTable,
            inventory.owner_id,
        )

        if material is None:
            raise ValueError(
                f"Material {inventory.owner_id} not found"
            )

        return (
            material.name,
            material.sku,
            material.unit_type,
        )

    product = await session.get(
        ProductTable,
        inventory.owner_id,
    )

    if product is None:
        raise ValueError(
            f"Product {inventory.owner_id} not found"
        )

    return (
        product.name,
        product.sku,
        UnitType.UNIT,
    )


async def seed_inventory_movements(
    session: AsyncSession,
) -> None:
    result = await session.execute(
        select(InventoryTable)
    )

    inventories = list(result.scalars().all())

    if not inventories:
        print("❌ No inventory records found.")
        return

    print(f"📦 Found {len(inventories)} inventory records.")

    now = datetime.now(timezone.utc)

    start_date = now - timedelta(days=180)

    # Make sure every inventory participates.
    base_movements = TOTAL_MOVEMENTS // len(inventories)
    remainder = TOTAL_MOVEMENTS % len(inventories)

    total_created = 0

    for index, inventory in enumerate(inventories):
        movements_count = base_movements

        if index < remainder:
            movements_count += 1

        owner_name, owner_code, unit_type = await get_owner_data(
            session,
            inventory,
        )

        current_quantity = Decimal(inventory.quantity)

        movement_times = sorted(
            random_created_at(
                start_date,
                now,
            )
            for _ in range(movements_count)
        )

        for created_at in movement_times:
            movement_type = random_movement_type(
                current_quantity,
                Decimal(inventory.minimum_quantity),
            )

            previous_quantity = current_quantity

            if movement_type == InventoryMovementType.ADJUSTMENT:

                new_quantity = generate_adjustment_quantity(
                    current_quantity,
                    Decimal(inventory.minimum_quantity),
                    unit_type,
                )

                movement_quantity = new_quantity

            else:

                movement_quantity = generate_quantity(
                    movement_type,
                    current_quantity,
                    unit_type,
                )

                if movement_type == InventoryMovementType.IN:
                    new_quantity = current_quantity + movement_quantity
                else:
                    new_quantity = current_quantity - movement_quantity

            movement = InventoryMovementTable(
                inventory_id=inventory.id,
                movement_type=movement_type,
                previous_quantity=previous_quantity,
                quantity=movement_quantity,
                new_quantity=new_quantity,
                owner_name=owner_name,
                owner_code=owner_code,
                unit_type=unit_type,
                reason=get_reason(
                    inventory.owner_type,
                    movement_type,
                ),
                created_at=created_at,
            )

            session.add(movement)

            current_quantity = new_quantity

            total_created += 1

        inventory.quantity = current_quantity

        if movement_times:
            inventory.last_movement_at = movement_times[-1]
        inventory.updated_at = now

    await session.commit()

    print(
        f"✅ Created {total_created} inventory movements."
    )


async def main():
    async with async_session_factory() as session:
        await seed_inventory_movements(session)


if __name__ == "__main__":
    asyncio.run(main())