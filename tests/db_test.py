from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.core.pydantic_test_settings import test_settings


database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=test_settings.POSTGRES_USER,
    password=test_settings.POSTGRES_PASSWORD,
    host=test_settings.POSTGRES_HOST,
    port=test_settings.POSTGRES_PORT,
    database=test_settings.POSTGRES_DB,
)


engine = create_async_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)