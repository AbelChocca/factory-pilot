from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.features.production_risk.repository import (
    ProductionAnalysisRepository,
)


def get_production_risk_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductionAnalysisRepository:

    return ProductionAnalysisRepository(
        session=session,
    )
