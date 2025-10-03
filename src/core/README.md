# Configuração do Home Finance Transaction Service

Este diretório contém as configurações centrais da aplicação home-finance-transaction-service.

## Arquivos

### config.py
Sistema de configuração principal baseado em Pydantic Settings que fornece:

- **Configurações por ambiente**: development, staging, production, testing
- **Validação automática**: Type hints e validação de valores
- **Variáveis de ambiente**: Suporta `.env` e variáveis de sistema
- **Cache**: Configurações são carregadas apenas uma vez durante a execução
- **Flexibilidade**: Configurações específicas por ambiente com herança

### schema.py
Definições de esquemas Pydantic para:

- **Transações**: Criação, atualização e resposta
- **Contas**: Criação, atualização e resposta  
- **Paginação**: Controle de páginas e filtros
- **Health check**: Status do serviço
- **Erros**: Estrutura padronizada de respostas de erro

## Como usar

### 1. Configurações básicas

```python
from src.core.config import settings

# Acessar configurações
print(f"Aplicação: {settings.app_name}")
print(f"Porta: {settings.port}")
print(f"Ambiente: {settings.environment}")
```

### 2. Configurações por ambiente

```python
from src.core.config import is_development, is_production

if is_development():
    # Lógica específica para desenvolvimento
    pass

if is_production():
    # Lógica específica para produção
    pass
```

### 3. Configurações do banco de dados

```python
from src.core.config import settings

# URL do banco
database_url = settings.database_url

# Configurações do pool
pool_size = settings.database_pool_size
max_overflow = settings.database_max_overflow
```

### 4. Schemas Pydantic

```python
from src.core.schema import TransactionCreate, TransactionResponse

# Criar uma transação
transaction_data = TransactionCreate(
    amount=Decimal("100.50"),
    description="Salário",
    transaction_type=TransactionType.INCOME,
    account_id=1
)

# Responder com dados formatados
response = TransactionResponse(
    id=1,
    amount=transaction_data.amount,
    description=transaction_data.description,
    # ... outros campos
)
```

## Variáveis de Ambiente

### Obrigatórias

- `DATABASE_URL`: URL de conexão com o banco de dados
- `SECRET_KEY`: Chave secreta com pelo menos 32 caracteres

### Opcionais (com valores padrão)

- `APP_NAME`: Nome da aplicação
- `ENVIRONMENT`: Ambiente de execução (development, staging, production, testing)
- `PORT`: Porta do servidor (padrão: 8000)
- `DEBUG`: Modo debug (padrão: False)
- `LOG_LEVEL`: Nível de log (padrão: INFO)

### Por Ambiente

As configurações podem ser ajustadas por ambiente usando prefixos:

- `DEV_` para development
- `STAGING_` para staging  
- `PROD_` para production
- `TEST_` para testing

Exemplo:
```bash
# Development
DEV_DEBUG=true
DEV_RELOAD=true

# Production
PROD_DEBUG=false
PROD_LOG_LEVEL=WARNING
```

## Exemplo de arquivo .env

```bash
# Configurações básicas
APP_NAME=Home Finance Transaction Service
ENVIRONMENT=development
DEBUG=true
PORT=8000

# Banco de dados
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/home_finance
SECRET_KEY=sua-chave-secreta-com-32-caracteres-minimo

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
```

## Validações Implementadas

### config.py
- URL do banco obrigatória
- Secret key com mínimo 32 caracteres
- Ambientes válidos: development, staging, production, testing
- Níveis de log válidos: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Parse automático de listas em variáveis CORS

### schema.py  
- Valores positivos para quantias
- Comprimento mínimo/máximo para strings
- Validação de enums para tipos e status
- Sanitização de tags (conversão para lowercase)

## Segurança

- Suporte a configurações específicas por ambiente
- Validação robusta de dados de entrada
- Type hints completo para melhor segurança de tipo
- Separação clara entre configurações públicas e privadas
- Prefixos específicos por ambiente para evitar conflitos

## Extensibilidade

- Fácil adição de novas configurações através de propriedades da classe `Settings`
- Suporte a novos ambientes através de subclassing
- Schemas modulares que podem ser importados conforme necessário
- Sistema de validação baseado em Pydantic para extensões customizadas
