"""
Configuracao de fixtures do pytest para testes
"""

import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.adapters.repositories.models import Base

# Configurar banco de testes
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-that-should-be-at-least-32-characters-long"


@pytest.fixture(scope="session")
def anyio_backend():
    """Define o backend assincrono para pytest-asyncio"""
    return "asyncio"


@pytest.fixture(scope="function", autouse=True)
async def clean_database():
    """Limpa o banco de dados antes de cada teste de integracao"""
    from src.adapters.repositories.models import Base
    from src.db.session import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup apos teste
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_session():
    """
    Fixture para criar uma sessao de banco de dados de teste em memoria

    Cria um banco SQLite em memoria para cada teste e destroi apos o teste
    """
    # Criar engine SQLite em memoria
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )

    # Criar todas as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Criar sessionmaker
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Fornecer sessao para o teste
    async with async_session_maker() as session:
        yield session

    # Cleanup: destruir todas as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def sample_transaction_data():
    """Dados de exemplo para criar transacao"""
    return {
        "data": "2025-01-15",
        "descricao": "Compra no mercado",
        "valor": 150.50,
        "tipo": "SAIDA",
        "categoria": "alimentacao"
    }


@pytest.fixture
def sample_local_data():
    """Dados de exemplo para criar local"""
    return {
        "nome_fantasia": "Supermercado Exemplo",
        "cnpj": "12345678000190",
        "razao_social": "Supermercado Exemplo LTDA",
        "categoria": "supermercado",
        "endereco": "Rua Exemplo, 123"
    }
