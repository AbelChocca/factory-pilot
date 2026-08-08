from app.features.products.repositories.product_repository import ProductRepository
from app.features.products.repositories.product_material_repository import (
    ProductMaterialRepository,
)

from app.db.dependencies import get_db_session

from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends

def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    return ProductRepository(
        session=session,
    )

def get_product_material_repository(
    session: AsyncSession = Depends(
        get_db_session,
    ),
) -> ProductMaterialRepository:

    return ProductMaterialRepository(
        session=session,
    )