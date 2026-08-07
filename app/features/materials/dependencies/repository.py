from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.features.materials.repository import MaterialRepository


def get_material_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MaterialRepository:
    return MaterialRepository(
        session=session,
    )