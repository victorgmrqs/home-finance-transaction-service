"""
Exemplos de uso das configurações e schemas
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List

# Exemplos de imports
from src.core.config import settings, is_development, is_production
from src.core.schema import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionListRequest,
    TransactionType,
    TransactionStatus,
    Currency,
    PaginationRequest,
    MonthlyOverviewResponse
)


def example_config_usage():
    """Exemplo de uso das configurações"""
    
    # Configurações básicas
    print(f"Aplicação: {settings.app_name}")
    print(f"Versão: {settings.app_version}")
    print(f"Ambiente: {settings.environment}")
    print(f"Debug: {settings.debug}")
    
    # Configurações específicas por ambiente
    if is_development():
        print("Modo desenvolvimento ativo")
        print(f"Nível de log: {settings.log_level}")
        print(f"Echo do banco: {settings.database_echo}")
    
    if is_production():
        print("Modo produção ativo")
        print(f"CORS Origins: {settings.cors_origins}")
    
    # Configurações de infraestrutura
    print(f"URL do banco: {settings.database_url}")
    print(f"Pool size: {settings.database_pool_size}")
    print(f"Max overflow: {settings.database_max_overflow}")
    
    # Configurações de segurança
    print(f"Secret key configurada: {bool(settings.secret_key)}")
    print(f"Token expire: {settings.access_token_expire_minutes} minutos")


def example_schema_usage():
    """Exemplos de uso dos schemas"""
    
    # Criando uma transação
    transaction = TransactionCreate(
        amount=Decimal("1000.00"),
        description="Salário mensal",
        transaction_type=TransactionType.INCOME,
        account_id=1,
        category="salário",
        tags=["work", "monthly"],
        currency=Currency.BRL
    )
    
    print("Transação criada:")
    print(f"Valor: {transaction.amount}")
    print(f"Descrição: {transaction.description}")
    print(f"Tipo: {transaction.transaction_type}")
    print(f"Moeda: {transaction.currency}")
    print(f"Tags: {transaction.tags}")
    
    # Simulando resposta da API
    response = TransactionResponse(
        id=1,
        amount=transaction.amount,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        transaction_date=transaction.transaction_date,
        category=transaction.category,
        tags=transaction.tags,
        currency=transaction.currency,
        account_id=transaction.account_id,
        status=TransactionStatus.COMPLETED,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    print("\nResposta da API:")
    print(f"ID: {response.id}")
    print(f"Status: {response.status}")
    print(f"Criado em: {response.created_at}")
    
    # Exemplo de busca com filtros
    search_request = TransactionListRequest(
        transaction_type=TransactionType.EXPENSE,
        category="alimentação",
        date_from=date(2024, 1, 1),
        date_to=date(2024, 12, 31),
        amount_min=Decimal("50.00"),
        amount_max=Decimal("500.00"),
        search="supermercado",
        pagination=PaginationRequest(page=1, size=20)
    )
    
    print("\nFiltros de busca:")
    print(f"Tipo: {search_request.transaction_type}")
    print(f"Categoria: {search_request.category}")
    print(f"Período: {search_request.date_from} a {search_request.date_to}")
    print(f"Valor: {search_request.amount_min} a {search_request.amount_max}")
    print(f"Página: {search_request.pagination.page}, Tamanho: {search_request.pagination.size}")


def example_environment_specific_config():
    """Exemplo de configurações específicas por ambiente"""
    
    # Estas seriam definidas no arquivo .env ou variáveis de sistema
    examples = {
        "development": {
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "sqlite+aiosqlite:///./dev.db",
            "RELOAD": "true"
        },
        "staging": {
            "ENVIRONMENT": "staging", 
            "DEBUG": "false",
            "LOG_LEVEL": "INFO",
            "DATABASE_URL": "postgresql+asyncpg://user:pass@staging-db:5432/app",
            "RELOAD": "false"
        },
        "production": {
            "ENVIRONMENT": "production",
            "DEBUG": "false", 
            "LOG_LEVEL": "WARNING",
            "DATABASE_URL": "postgresql+asyncpg://user:pass@prod-db:5432/app",
            "RELOAD": "false"
        },
        "testing": {
            "ENVIRONMENT": "testing",
            "DEBUG": "false",
            "LOG_LEVEL": "DEBUG", 
            "DATABASE_URL": "sqlite+aiosqlite:///./test.db",
            "RELOAD": "false"
        }
    }
    
    print("Exemplos de configurações por ambiente:")
    for env, vars in examples.items():
        print(f"\n{env.upper()}:")
        for key, value in vars.items():
            print(f"  {key}={value}")


def example_fastapi_integration():
    """Exemplo de integração com FastAPI"""
    
    # Exemplo de como usar nas rotas do FastAPI
    from fastapi import FastAPI, Depends, HTTPException
    from src.db.session import get_session
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # app = FastAPI(
    #     title=settings.app_name,
    #     version=settings.app_version,
    #     debug=settings.debug
    # )
    
    # @app.get("/health")
    # async def health_check():
    #     return {
    #         "status": "ok",
    #         "environment": settings.environment,
    #         "version": settings.app_version
    #     }
    
    # @app.post("/transactions",
    #     response_model=TransactionResponse,
    #     tags=["Transactions"]
    # )
    # async def create_transaction(
    #     transaction: TransactionCreate,
    #     session: AsyncSession = Depends(get_session)
    # ):
    #     # Lógica de criação da transação
    #     pass
    
    print("Exemplo de integração com FastAPI (comentado)")
    print("- Usar settings para configurar a aplicação")
    print("- Usar schemas para validação e resposta")
    print("- Usar dependências para injeção de configurações")


if __name__ == "__main__":
    print("=== EXEMPLOS DE USO ===\n")
    
    print("1. Configurações:")
    example_config_usage()
    
    print("\n2. Schemas:")
    example_schema_usage()
    
    print("\n3. Configurações por ambiente:")
    example_environment_specific_config()
    
    print("\n4. Integração FastAPI:")
    example_fastapi_integration()
    
    print("\n=== FIM DOS EXEMPLOS ===")
