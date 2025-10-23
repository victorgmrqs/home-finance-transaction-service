# 🏗️ Arquitetura - Home Finance Transaction Service

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Clean Architecture](#clean-architecture)
- [Camadas da Aplicação](#camadas-da-aplicação)
- [Fluxo de Dados](#fluxo-de-dados)
- [Padrões de Projeto](#padrões-de-projeto)
- [Decisões Arquiteturais](#decisões-arquiteturais)
- [Diagramas](#diagramas)

---

## Visão Geral

O **Home Finance Transaction Service** segue os princípios de **Clean Architecture** (Arquitetura Limpa) combinada com **Hexagonal Architecture** (Ports & Adapters), promovendo:

- ✅ **Separação de Responsabilidades**
- ✅ **Independência de Frameworks**
- ✅ **Testabilidade**
- ✅ **Manutenibilidade**
- ✅ **Escalabilidade**

### Princípios Fundamentais

1. **Dependency Inversion**: Dependências apontam para abstrações (Ports)
2. **Domain-Driven Design**: Lógica de negócio no domínio
3. **SOLID Principles**: Código limpo e coeso
4. **Single Responsibility**: Cada módulo tem uma responsabilidade única

---

## Clean Architecture

### Estrutura em Camadas

```
┌─────────────────────────────────────────────────────────┐
│                    ADAPTERS                             │
│  (Controllers, Repositories, Presenters, Middlewares)   │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │              APPLICATION                          │ │
│  │         (Use Cases / Services)                    │ │
│  │                                                   │ │
│  │  ┌─────────────────────────────────────────────┐ │ │
│  │  │           DOMAIN                            │ │ │
│  │  │    (Entities, Business Rules)               │ │ │
│  │  │                                             │ │ │
│  │  └─────────────────────────────────────────────┘ │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘

Dependências fluem de fora para dentro:
Adapters → Application → Domain
```

### Regras de Dependência

1. **Domain** não depende de nada (código puro Python)
2. **Application** depende apenas do **Domain** e **Ports**
3. **Adapters** implementam **Ports** e dependem de **Application**
4. **Ports** definem interfaces (contratos abstratos)

---

## Camadas da Aplicação

### 1. Domain Layer (Núcleo)

**Localização**: `src/domain/`

**Responsabilidade**: Regras de negócio puras

**Componentes**:
- **Entities**: Objetos de negócio (Transaction, Painel, Usuario)
- **Value Objects**: Enums (TransactionType, Recurrence, TipoDivisao)
- **Domain Services**: Lógica de negócio complexa
- **Exceptions**: Exceções de domínio

**Exemplo**:
```python
# src/domain/models/transaction.py

@dataclass
class Transaction:
    """Entidade de domínio pura"""

    id: Optional[int]
    valor: Decimal
    descricao: str

    def __post_init__(self):
        """Validações de negócio"""
        if self.valor <= 0:
            raise ValueError("Valor deve ser positivo")

    def is_parcelada(self) -> bool:
        """Regra de negócio"""
        return self.parcelas is not None and self.parcelas > 1
```

**Características**:
- ✅ Sem dependências externas
- ✅ Testável isoladamente
- ✅ Código agnóstico a frameworks
- ✅ Validações de negócio encapsuladas

---

### 2. Application Layer (Casos de Uso)

**Localização**: `src/application/`

**Responsabilidade**: Orquestrar casos de uso

**Componentes**:
- **Services**: Casos de uso da aplicação
- **DTOs**: Objetos de transferência de dados (opcional)

**Exemplo**:
```python
# src/application/transaction_service.py

class TransactionService:
    """Orquestra casos de uso de transações"""

    def __init__(self, repository: ITransactionRepository):
        self.repository = repository  # Dependência de interface

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Caso de uso: Criar transação"""
        # Validação já ocorre na entidade
        return await self.repository.create(transaction)

    async def list_transactions(...) -> tuple[List[Transaction], int]:
        """Caso de uso: Listar transações com filtros"""
        transactions = await self.repository.list_all(...)
        total = await self.repository.count(...)
        return transactions, total
```

**Características**:
- ✅ Depende apenas de **Domain** e **Ports**
- ✅ Não conhece detalhes de infraestrutura
- ✅ Coordena entidades de domínio
- ✅ Testável com mocks

---

### 3. Ports Layer (Interfaces)

**Localização**: `src/ports/`

**Responsabilidade**: Definir contratos (abstrações)

**Exemplo**:
```python
# src/ports/transaction_port.py

from abc import ABC, abstractmethod

class ITransactionRepository(ABC):
    """Interface do repositório (contrato)"""

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Contrato: criar transação"""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Transaction]:
        """Contrato: buscar por ID"""
        pass
```

**Características**:
- ✅ Define **O QUE** fazer, não **COMO** fazer
- ✅ Permite substituir implementações
- ✅ Facilita testes com mocks
- ✅ Inversão de Dependência (SOLID)

---

### 4. Adapters Layer (Implementações)

**Localização**: `src/adapters/`

**Responsabilidade**: Implementar infraestrutura

#### 4.1 Controllers (HTTP)

**Localização**: `src/adapters/controllers/`

**Responsabilidade**: Receber requisições HTTP

**Exemplo**:
```python
# src/adapters/controllers/transaction_controller.py

@router.post("/transactions")
async def create_transaction(
    request: TransactionCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    # 1. Converter request para entidade
    transaction = Transaction(...)

    # 2. Executar caso de uso
    repository = TransactionRepository(session)
    service = TransactionService(repository)
    created = await service.create_transaction(transaction)

    # 3. Formatar resposta
    return present_transaction_created(created)
```

**Características**:
- ✅ Conhece FastAPI
- ✅ Não contém lógica de negócio
- ✅ Delega para Application Layer
- ✅ Usa Presenters para formatar resposta

#### 4.2 Repositories (Database)

**Localização**: `src/adapters/repositories/`

**Responsabilidade**: Acesso a dados

**Exemplo**:
```python
# src/adapters/repositories/transaction_repository.py

class TransactionRepository(ITransactionRepository):
    """Implementa ITransactionRepository usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TransactionModel) -> Transaction:
        """Converte ORM Model → Domain Entity"""
        return Transaction(...)

    def _to_model(self, transaction: Transaction) -> TransactionModel:
        """Converte Domain Entity → ORM Model"""
        return TransactionModel(...)

    async def create(self, transaction: Transaction) -> Transaction:
        model = self._to_model(transaction)
        self.session.add(model)
        await self.session.commit()
        return self._to_domain(model)
```

**Características**:
- ✅ Implementa Port (interface)
- ✅ Conhece SQLAlchemy
- ✅ Faz conversões Domain ↔ ORM
- ✅ Isola lógica de persistência

#### 4.3 Presenters (Response Formatting)

**Localização**: `src/adapters/presenters/`

**Responsabilidade**: Formatar respostas HTTP

**Exemplo**:
```python
# src/adapters/presenters/transaction_presenter.py

def present_transaction(transaction: Transaction) -> dict:
    """Formata entidade para resposta JSON"""
    return {
        "id": transaction.id,
        "valor": float(transaction.valor),
        "descricao": transaction.descricao,
        "tipo_divisao": transaction.tipo_divisao.value
    }

def present_transaction_created(transaction: Transaction) -> dict:
    return success_response(
        code="TRANSACTION_CREATED",
        message="Transação criada com sucesso",
        data=present_transaction(transaction)
    )
```

**Características**:
- ✅ Separa formatação de lógica
- ✅ Padroniza respostas
- ✅ Facilita mudanças no formato de API

#### 4.4 Middlewares

**Localização**: `src/adapters/middlewares/`

**Responsabilidade**: Interceptar requisições

**Exemplo**:
```python
# src/adapters/middlewares/auth_middleware.py

class MockAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Autenticação mock para desenvolvimento
        user_id = request.headers.get("X-User-ID", "1")
        request.state.usuario_id = int(user_id)
        return await call_next(request)
```

---

## Fluxo de Dados

### Fluxo de Requisição (Create Transaction)

```
1. HTTP POST /api/v1/transactions
   ↓
2. Controller (transaction_controller.py)
   - Recebe TransactionCreateRequest (Pydantic)
   - Valida dados (Pydantic automático)
   ↓
3. Converte Request → Domain Entity
   - TransactionCreateRequest → Transaction
   ↓
4. Application Service (transaction_service.py)
   - Executa caso de uso: create_transaction()
   - Valida regras de negócio (Domain)
   ↓
5. Port Interface (transaction_port.py)
   - Chama ITransactionRepository.create()
   ↓
6. Repository (transaction_repository.py)
   - Converte Transaction → TransactionModel (ORM)
   - Persiste no banco via SQLAlchemy
   - Converte TransactionModel → Transaction
   ↓
7. Volta para Application Service
   - Retorna Transaction criada
   ↓
8. Presenter (transaction_presenter.py)
   - Formata Transaction → JSON Response
   ↓
9. Controller retorna HTTP 201 Created
```

### Fluxo de Consulta (List Transactions)

```
1. HTTP GET /api/v1/transactions?painel_id=1&tipo=SAIDA
   ↓
2. Controller extrai query params
   ↓
3. Application Service
   - list_transactions(painel_id, tipo, ...)
   ↓
4. Repository
   - list_all() → SELECT FROM transacoes WHERE ...
   - count() → SELECT COUNT(*) WHERE ...
   ↓
5. Converte List[TransactionModel] → List[Transaction]
   ↓
6. Presenter formata lista
   ↓
7. HTTP 200 OK com JSON
```

---

## Padrões de Projeto

### 1. Repository Pattern

**Objetivo**: Abstrair acesso a dados

**Implementação**:
```python
# Port (Interface)
class ITransactionRepository(ABC):
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        pass

# Adapter (Implementação)
class TransactionRepository(ITransactionRepository):
    async def create(self, transaction: Transaction) -> Transaction:
        # Implementação com SQLAlchemy
        pass
```

**Benefícios**:
- ✅ Trocar banco de dados sem afetar Application
- ✅ Testar com repositório em memória
- ✅ Separar lógica de persistência

---

### 2. Dependency Injection

**Objetivo**: Inverter dependências

**Implementação**:
```python
# Service recebe dependência via construtor
class TransactionService:
    def __init__(self, repository: ITransactionRepository):
        self.repository = repository  # Depende de abstração

# Controller injeta dependência
repository = TransactionRepository(session)
service = TransactionService(repository)  # DI manual
```

**Benefícios**:
- ✅ Baixo acoplamento
- ✅ Fácil testar (injetar mock)
- ✅ Substituir implementações

---

### 3. Presenter Pattern

**Objetivo**: Separar formatação de resposta

**Implementação**:
```python
def present_transaction_created(transaction: Transaction) -> dict:
    return {
        "code": "TRANSACTION_CREATED",
        "message": "Transação criada",
        "data": present_transaction(transaction)
    }
```

**Benefícios**:
- ✅ Padronizar respostas
- ✅ Separar formatação de lógica
- ✅ Facilitar mudanças de API

---

### 4. Factory Pattern

**Objetivo**: Criar objetos complexos

**Implementação**:
```python
# src/db/session.py

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Factory para sessões de banco"""
    async with async_session_maker() as session:
        yield session
```

**Benefícios**:
- ✅ Centralizar criação
- ✅ Gerenciar lifecycle
- ✅ Facilitar testes

---

## Decisões Arquiteturais

### ADR-001: Adoção de Clean Architecture

**Status**: ✅ Aceito

**Contexto**: Necessidade de código manutenível e testável

**Decisão**: Implementar Clean Architecture com Ports & Adapters

**Consequências**:
- ✅ Código mais organizado
- ✅ Fácil testar
- ⚠️ Curva de aprendizado inicial
- ⚠️ Mais arquivos/pastas

---

### ADR-002: Separação de Controllers por Responsabilidade

**Status**: ✅ Aceito (implementado 2025-10-22)

**Contexto**: `painel_controller.py` tinha 508 linhas com múltiplas responsabilidades

**Decisão**: Separar em:
- `painel_controller.py` (CRUD apenas)
- `painel_sharing_controller.py` (Compartilhamento)
- `painel_analytics_controller.py` (Analytics)

**Consequências**:
- ✅ SRP (Single Responsibility Principle)
- ✅ Controllers menores e focados
- ✅ Melhor organização no Swagger
- ✅ Mais fácil manter e testar

---

### ADR-003: Async/Await em Todo o Stack

**Status**: ✅ Aceito

**Contexto**: Operações I/O (database, HTTP) bloqueantes

**Decisão**: Usar async/await com SQLAlchemy async

**Consequências**:
- ✅ Melhor performance
- ✅ Suporta mais requisições concorrentes
- ⚠️ Toda chain deve ser async

---

## Diagramas

### Diagrama de Camadas

```
┌────────────────────────────────────────────┐
│           HTTP Layer (FastAPI)             │
│  ┌──────────────────────────────────────┐  │
│  │  Controllers                         │  │
│  │  - transaction_controller.py         │  │
│  │  - painel_controller.py              │  │
│  │  - painel_sharing_controller.py      │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│       Application Layer (Use Cases)        │
│  ┌──────────────────────────────────────┐  │
│  │  Services                            │  │
│  │  - transaction_service.py            │  │
│  │  - painel_service.py                 │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│         Ports Layer (Interfaces)           │
│  ┌──────────────────────────────────────┐  │
│  │  - ITransactionRepository            │  │
│  │  - IPainelRepository                 │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│      Infrastructure Layer (Adapters)       │
│  ┌──────────────────────────────────────┐  │
│  │  Repositories                        │  │
│  │  - TransactionRepository (SQLAlchemy)│  │
│  │  - PainelRepository (SQLAlchemy)     │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│            Database (SQLite)               │
└────────────────────────────────────────────┘
```

### Diagrama de Fluxo (Create Transaction)

```
Client                Controller           Service          Repository       Database
  │                      │                    │                 │               │
  │──POST /transactions─>│                    │                 │               │
  │                      │                    │                 │               │
  │                      │─create_transaction>│                 │               │
  │                      │    (Transaction)   │                 │               │
  │                      │                    │─create()───────>│               │
  │                      │                    │  (Transaction)  │               │
  │                      │                    │                 │─INSERT INTO──>│
  │                      │                    │                 │               │
  │                      │                    │                 │<──Model───────│
  │                      │                    │<─Transaction────│               │
  │                      │<───Transaction─────│                 │               │
  │                      │                    │                 │               │
  │<────201 Created──────│                    │                 │               │
  │  (JSON Response)     │                    │                 │               │
```

---

## Benefícios da Arquitetura

### Testabilidade

```python
# Testar Application Service com mock de repository
class MockRepository(ITransactionRepository):
    async def create(self, transaction):
        return transaction

service = TransactionService(MockRepository())
# Testar sem banco de dados real
```

### Manutenibilidade

- ✅ Mudanças isoladas por camada
- ✅ Fácil encontrar código
- ✅ Substituir implementações

### Escalabilidade

- ✅ Adicionar novos casos de uso
- ✅ Trocar banco de dados
- ✅ Adicionar cache
- ✅ Microserviços futuros

---

**Última Atualização:** 2025-10-22
**Versão:** 0.1.0
**Arquiteto:** Clean Architecture + DDD
