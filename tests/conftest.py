"""Pytest configuration and fixtures for testing."""

import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from src.db.session import get_db
from src.models.subnet import Base as SubnetBase
from src.models.flow_snapshot import Base as FlowSnapshotBase
from src.models.signal import Base as SignalBase
from src.models.report import Base as ReportBase

# Create in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create async engine for test database (function-scoped for isolation)."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SubnetBase.metadata.create_all)
        await conn.run_sync(FlowSnapshotBase.metadata.create_all)
        await conn.run_sync(SignalBase.metadata.create_all)
        await conn.run_sync(ReportBase.metadata.create_all)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SubnetBase.metadata.drop_all)
        await conn.run_sync(FlowSnapshotBase.metadata.drop_all)
        await conn.run_sync(SignalBase.metadata.drop_all)
        await conn.run_sync(ReportBase.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create a test database session."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency with test session."""

    async def _get_db():
        yield db_session

    return _get_db
