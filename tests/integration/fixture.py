import pytest
from tests.utils import docker_utils
from tests.utils import database_utils

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from httpx import AsyncClient, ASGITransport
from src import app
from src.db.main import get_session
import asyncio
from unittest.mock import AsyncMock


from src.config import config_obj

# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session", autouse=True)
async def db_session_integration():
    # Start the database container
    container = docker_utils.start_database_container()

    # Create an async engine
    async_engine = create_async_engine(
        config_obj.TEST_DATABASE_URL,
        echo=True
    )

    async with async_engine.connect() as connection:
        await database_utils.migrate_to_db("migrations", "alembic.ini", connection)

    session_maker = sessionmaker(autocommit=False, autoflush=True, bind=async_engine, class_=AsyncSession)

    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

    # stopping the container once test is done
    try:
        container.stop()
        container.remove()
    except Exception as e:
        print('container not found')

    # Dispose the async engine
    await async_engine.dispose()


@pytest.fixture(scope='function')
async def client(db_session_integration):
    app.dependency_overrides[get_session] = lambda: db_session_integration
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://localhost') as client:
        yield client
