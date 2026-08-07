from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel

from app.core.pydantic_settings import settings


engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)