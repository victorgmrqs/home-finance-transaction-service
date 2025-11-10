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


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """
    Setup inicial do banco de dados - cria tabelas uma vez para toda a sessão de testes.
    Isso melhora significativamente a performance ao evitar criar/dropar tabelas para cada teste.
    """
    from src.adapters.repositories.models import Base
    from src.db.session import engine

    # Criar todas as tabelas uma vez
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup final - dropar todas as tabelas ao final de todos os testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(setup_database):
    """
    Limpa o banco de dados antes e depois de cada teste.

    Usa DELETE rápido ao invés de DROP/CREATE para melhor performance.
    Mantém a estrutura das tabelas e apenas limpa os dados.
    """
    from src.adapters.repositories.models import Base
    from src.db.session import engine

    yield

    # Cleanup apos teste - limpar dados mas manter estrutura para performance
    # Usar DELETE ao invés de DROP/CREATE para melhor performance
    try:
        async with engine.begin() as conn:
            # Limpar dados de todas as tabelas em ordem reversa (respeitando foreign keys)
            # Isso é muito mais rápido que DROP/CREATE
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    await conn.execute(table.delete())
                except Exception:
                    # Ignorar erros se a tabela não existir ou não tiver dados
                    pass
    except Exception:
        # Se falhar, pode ser que o engine não esteja inicializado
        # Isso é OK para testes unitários que não usam banco
        pass


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
