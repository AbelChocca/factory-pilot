from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.features.suppliers.repositories.supplier_repository import SupplierRepository
from app.features.suppliers.repositories.supplier_material_repository import (
    SupplierMaterialRepository,
)


def get_supplier_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SupplierRepository:
    return SupplierRepository(
        session=session,
    )

def get_supplier_material_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SupplierMaterialRepository:
    return SupplierMaterialRepository(
        session=session,
    )