from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import func, select, case, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.suppliers.models.supplier import SupplierTable
from app.features.suppliers.models.supplier_material import SupplierMaterialTable
from app.features.materials.model import MaterialTable
from app.features.inventory.models.inventory import InventoryTable
from app.features.inventory.types import InventoryOwnerType
from app.shared.enums import Status


@dataclass
class SupplierRiskRow:
    supplier_id: UUID
    supplier_name: str
    lead_time_days: int
    supplied_materials: int
    at_risk_materials: int


class SupplierRiskRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_supplier_risk_data(
        self,
    ) -> list[SupplierRiskRow]:

        statement = (
            select(
                SupplierTable.id,
                SupplierTable.name,
                SupplierTable.lead_time_days,
                func.count(
                    SupplierMaterialTable.material_id
                ).label("supplied_materials"),
                func.count(
                    case(
                        (
                            and_(
                                InventoryTable.quantity
                                <= InventoryTable.minimum_quantity,
                                InventoryTable.quantity > 0,
                            ),
                            1,
                        )
                    )
                ).label("at_risk_materials"),
            )
            .join(
                SupplierMaterialTable,
                SupplierMaterialTable.supplier_id
                == SupplierTable.id,
            )
            .join(
                MaterialTable,
                MaterialTable.id
                == SupplierMaterialTable.material_id,
            )
            .outerjoin(
                InventoryTable,
                and_(
                    InventoryTable.owner_id
                    == MaterialTable.id,
                    InventoryTable.owner_type
                    == InventoryOwnerType.MATERIAL,
                ),
            )
            .where(
                SupplierTable.status == Status.ACTIVE,
                MaterialTable.status == Status.ACTIVE,
            )
            .group_by(
                SupplierTable.id,
                SupplierTable.name,
                SupplierTable.lead_time_days,
            )
        )

        result = await self.session.execute(statement)

        rows = result.all()

        return [
            SupplierRiskRow(
                supplier_id=row.id,
                supplier_name=row.name,
                lead_time_days=row.lead_time_days,
                supplied_materials=row.supplied_materials,
                at_risk_materials=row.at_risk_materials,
            )
            for row in rows
        ]