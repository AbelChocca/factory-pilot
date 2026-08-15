from dataclasses import dataclass
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType


@dataclass
class InventoryHealthCounts:
    total: int
    available: int
    low_stock: int
    out_of_stock: int


class InventoryHealthRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_health_counts(
        self,
        owner_type: InventoryOwnerType,
    ) -> InventoryHealthCounts:

        statement = select(
            func.count(InventoryTable.id).label(
                "total"
            ),
            func.sum(
                case(
                    (
                        InventoryTable.quantity > 0,
                        case(
                            (
                                InventoryTable.quantity
                                <= InventoryTable.minimum_quantity,
                                0,
                            ),
                            else_=1,
                        ),
                    ),
                    else_=0,
                )
            ).label("available"),
            func.sum(
                case(
                    (
                        (
                            InventoryTable.quantity > 0
                        )
                        & (
                            InventoryTable.quantity
                            <= InventoryTable.minimum_quantity
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("low_stock"),
            func.sum(
                case(
                    (
                        InventoryTable.quantity <= 0,
                        1,
                    ),
                    else_=0,
                )
            ).label("out_of_stock"),
        ).where(
            InventoryTable.owner_type == owner_type,
        )

        result = await self.session.execute(
            statement,
        )

        row = result.one()

        return InventoryHealthCounts(
            total=row.total or 0,
            available=row.available or 0,
            low_stock=row.low_stock or 0,
            out_of_stock=row.out_of_stock or 0,
        )