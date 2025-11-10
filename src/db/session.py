from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.config import settings

# Configurações do engine do banco de dados
if "sqlite" in settings.database_url:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
else:
    # Para outros bancos (PostgreSQL, MySQL), usar pool
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Factory de sessão do SQLAlchemy"""
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()
