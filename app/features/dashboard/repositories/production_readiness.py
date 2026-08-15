from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.products.models.product import ProductTable


class ProductionReadinessRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def count_products(self) -> int:
        statement = select(
            func.count(ProductTable.id)
        )

        result = await self.session.execute(
            statement,
        )

        return result.scalar_one()