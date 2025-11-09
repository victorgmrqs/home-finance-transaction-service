from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.config import settings

# Configurações do engine do banco de dados
engine_kwargs = {
    "url": settings.database_url,
    "echo": settings.database_echo,
}

# Para SQLite, usar configurações específicas
if "sqlite" in settings.database_url:
    engine_kwargs.update({
        "poolclass": StaticPool,
        "connect_args": {"check_same_thread": False},
    })
else:
    # Para outros bancos (PostgreSQL, MySQL), usar pool
    engine_kwargs.update({
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
    })

engine = create_async_engine(**engine_kwargs)


async def get_session() -> AsyncSession:
    """Factory de sessão do SQLAlchemy"""
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()
