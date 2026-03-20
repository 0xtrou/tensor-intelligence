from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings

engine = create_async_engine(
    settings.DATABASE_URL, echo=False, pool_size=10, max_overflow=20
)
async_sessionmaker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with async_sessionmaker() as session:
        yield session
