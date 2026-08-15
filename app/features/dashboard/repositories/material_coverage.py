from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.enums import Status

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType, InventoryMovementType
from app.features.inventory.models.inventory_movement import (
    InventoryMovementTable,
)
from app.features.materials.model import MaterialTable

from dataclasses import dataclass


@dataclass
class MaterialInventoryRow:
    material_id: UUID
    material_name: str
    material_sku: str
    current_stock: Decimal


@dataclass
class MaterialMovementSummaryRow:
    material_id: UUID
    total_outbound: Decimal

class MaterialCoverageRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_material_inventory(
        self,
    ) -> list[MaterialInventoryRow]:

        statement = (
            select(
                MaterialTable.id.label(
                    "material_id",
                ),
                MaterialTable.name.label(
                    "material_name",
                ),
                MaterialTable.sku.label(
                    "material_sku",
                ),
                InventoryTable.quantity.label(
                    "current_stock",
                ),
            )
            .join(
                InventoryTable,
                (
                    InventoryTable.owner_id
                    == MaterialTable.id
                )
                & (
                    InventoryTable.owner_type
                    == InventoryOwnerType.MATERIAL
                ),
            )
            .where(
                MaterialTable.status == Status.ACTIVE,
            )
        )

        result = await self.session.execute(
            statement,
        )

        rows = result.all()

        return [
            MaterialInventoryRow(
                material_id=row.material_id,
                material_name=row.material_name,
                material_sku=row.material_sku,
                current_stock=row.current_stock,
            )
            for row in rows
        ]

    async def get_material_movement_summary(
        self,
        since: datetime,
    ) -> list[MaterialMovementSummaryRow]:

        statement = (
            select(
                InventoryTable.owner_id.label(
                    "material_id",
                ),
                func.coalesce(
                    func.sum(
                        InventoryMovementTable.quantity
                    ),
                    Decimal("0"),
                ).label(
                    "total_outbound",
                ),
            )
            .join(
                InventoryTable,
                InventoryTable.id
                == InventoryMovementTable.inventory_id,
            )
            .where(
                InventoryTable.owner_type
                == InventoryOwnerType.MATERIAL,
                InventoryMovementTable.movement_type
                == InventoryMovementType.OUT,
                InventoryMovementTable.created_at
                >= since,
            )
            .group_by(
                InventoryTable.owner_id,
            )
        )

        result = await self.session.execute(
            statement,
        )

        rows = result.all()

        return [
            MaterialMovementSummaryRow(
                material_id=row.material_id,
                total_outbound=row.total_outbound,
            )
            for row in rows
        ]