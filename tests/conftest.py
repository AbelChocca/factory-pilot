import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.features.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.features.inventory.services.inventory_service import InventoryService

from tests.db_test import engine


@pytest_asyncio.fixture(
    scope="function",
    autouse=True,
)
async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(
            SQLModel.metadata.drop_all,
        )

        await connection.run_sync(
            SQLModel.metadata.create_all,
        )

    yield


@pytest_asyncio.fixture
async def db_session():
    async with engine.connect() as connection:
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def inventory_service(
    db_session: AsyncSession,
) -> InventoryService:

    inventory_repository = InventoryRepository(
        session=db_session,
    )

    return InventoryService(
        inventory_repository=inventory_repository,
    )