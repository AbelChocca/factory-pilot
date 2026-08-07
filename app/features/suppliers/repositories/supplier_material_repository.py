from uuid import UUID

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.suppliers.models.supplier import SupplierTable
from app.features.materials.model import MaterialTable
from app.features.suppliers.models.supplier_material import SupplierMaterialTable
from app.features.suppliers.schemas.supplier_material import MaterialSupplierResponse, SupplierMaterialResponse, MaterialSupplierDetailResponse


class SupplierMaterialRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_material_ids(
        self,
        material_ids: list[UUID],
    ) -> list[MaterialSupplierDetailResponse]:

        statement = (
            select(
                SupplierMaterialTable,
                SupplierTable,
                MaterialTable
            )
            .join(
                MaterialTable,
                MaterialTable.id == SupplierMaterialTable.material_id,
            )
            .join(
                SupplierTable,
                SupplierTable.id == SupplierMaterialTable.supplier_id,
            )
            .where(
                SupplierMaterialTable.material_id.in_(material_ids)
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialSupplierDetailResponse(
                material_id=relation.material_id,
                material_name=material.name,
                material_sku=material.sku,
                unit_type=material.unit_type,
                supplier_id=relation.supplier_id,
                supplier_name=supplier.name,
                supplier_sku=relation.supplier_sku,
                lead_time_days=supplier.lead_time_days,
                unit_price=relation.unit_price,
                preferred=relation.preferred,
            )
            for relation, supplier, material in result.all()
        ]

    async def count(self) -> int:
        statement = select(func.count()).select_from(
            SupplierMaterialTable
        )

        result = await self.session.execute(statement)

        return result.scalar_one()

    async def save(
        self,
        supplier_material: SupplierMaterialTable,
    ) -> SupplierMaterialTable:
        self.session.add(supplier_material)

        await self.session.commit()
        await self.session.refresh(supplier_material)

        return supplier_material

    async def save_all(
        self,
        supplier_materials: list[SupplierMaterialTable],
    ) -> None:
        self.session.add_all(supplier_materials)

        await self.session.commit()

    async def get_by_material_id(
        self,
        material_id: UUID,
    ) -> list[MaterialSupplierResponse]:

        statement = (
            select(
                SupplierMaterialTable,
                SupplierTable,
            )
            .join(
                SupplierTable,
                SupplierTable.id == SupplierMaterialTable.supplier_id,
            )
            .where(
                SupplierMaterialTable.material_id == material_id
            )
            .order_by(
                SupplierMaterialTable.preferred.desc(),
                SupplierTable.name,
            )
        )

        result = await self.session.execute(statement)

        return [
            MaterialSupplierResponse(
                supplier_id=supplier.id,
                supplier_name=supplier.name,
                supplier_email=supplier.email,
                supplier_phone=supplier.phone,
                lead_time_days=supplier.lead_time_days,
                supplier_sku=relation.supplier_sku,
                unit_price=relation.unit_price,
                preferred=relation.preferred,
            )
            for relation, supplier in result.all()
        ]

    async def get_by_supplier_id(
        self,
        supplier_id: UUID,
    ) -> list[SupplierMaterialResponse]:

        statement = (
            select(
                SupplierMaterialTable,
                MaterialTable,
            )
            .join(
                MaterialTable,
                MaterialTable.id == SupplierMaterialTable.material_id,
            )
            .where(
                SupplierMaterialTable.supplier_id == supplier_id
            )
            .order_by(
                MaterialTable.name,
            )
        )

        result = await self.session.execute(statement)

        return [
            SupplierMaterialResponse(
                material_id=material.id,
                material_name=material.name,
                material_sku=material.sku,
                material_type=material.material_type,
                unit_type=material.unit_type,
                supplier_sku=relation.supplier_sku,
                unit_price=relation.unit_price,
                preferred=relation.preferred,
            )
            for relation, material in result.all()
        ]

    async def get_by_supplier_and_material(
        self,
        supplier_id: UUID,
        material_id: UUID,
    ) -> SupplierMaterialTable | None:

        statement = (
            select(SupplierMaterialTable)
            .where(
                and_(
                    SupplierMaterialTable.supplier_id == supplier_id,
                    SupplierMaterialTable.material_id == material_id,
                )
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_preferred_supplier(
        self,
        material_id: UUID,
    ) -> MaterialSupplierResponse | None:

        statement = (
            select(
                SupplierMaterialTable,
                SupplierTable,
            )
            .join(
                SupplierTable,
                SupplierTable.id == SupplierMaterialTable.supplier_id,
            )
            .where(
                and_(
                    SupplierMaterialTable.material_id == material_id,
                    SupplierMaterialTable.preferred.is_(True),
                )
            )
        )

        result = await self.session.execute(statement)

        row = result.first()

        if row is None:
            return None

        relation, supplier = row

        return MaterialSupplierResponse(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            supplier_email=supplier.email,
            supplier_phone=supplier.phone,
            lead_time_days=supplier.lead_time_days,
            supplier_sku=relation.supplier_sku,
            unit_price=relation.unit_price,
            preferred=relation.preferred,
        )

    async def delete(
        self,
        supplier_id: UUID,
        material_id: UUID,
    ) -> bool:

        statement = (
            delete(SupplierMaterialTable)
            .where(
                and_(
                    SupplierMaterialTable.supplier_id == supplier_id,
                    SupplierMaterialTable.material_id == material_id,
                )
            )
        )

        result = await self.session.execute(statement)

        await self.session.commit()

        return result.rowcount > 0

    async def delete_by_material_id(
        self,
        material_id: UUID,
    ) -> None:

        statement = (
            delete(SupplierMaterialTable)
            .where(
                SupplierMaterialTable.material_id == material_id
            )
        )

        await self.session.execute(statement)
        await self.session.commit()

    async def delete_by_supplier_id(
        self,
        supplier_id: UUID,
    ) -> None:

        statement = (
            delete(SupplierMaterialTable)
            .where(
                SupplierMaterialTable.supplier_id == supplier_id
            )
        )

        await self.session.execute(statement)
        await self.session.commit()