# 🛠️ Guia de Desenvolvimento - Home Finance Transaction Service

## 📋 Índice

- [Requisitos](#-requisitos)
- [Setup Inicial](#-setup-inicial)
- [Executando o Projeto](#-executando-o-projeto)
- [Estrutura do Código](#-estrutura-do-código)
- [Criando Novos Endpoints](#-criando-novos-endpoints)
- [Trabalhando com Banco de Dados](#-trabalhando-com-banco-de-dados)
- [Testes](#-testes)
- [Boas Práticas](#-boas-práticas)
- [Troubleshooting](#-troubleshooting)

---

## 🔧 Requisitos

### Obrigatórios
- **Python 3.12+**
- **uv** (gerenciador de dependências)

### Instalação do UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## 🚀 Setup Inicial

### 1. Clone e Instale Dependências

```bash
# Clone o repositório
git clone <repo-url>
cd home-finance-transaction-service

# Instale dependências
uv sync

# Verifique instalação
uv run python --version  # Deve mostrar Python 3.12+
```

### 2. Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados
DATABASE_URL=sqlite+aiosqlite:///./home_finance.db

# Segurança
SECRET_KEY=your-super-secret-key-min-32-chars-here

# Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Servidor
HOST=0.0.0.0
PORT=8000

# CORS (separado por vírgulas)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Execute Migrações

```bash
# Primeira vez: inicializar Alembic (se necessário)
uv run alembic init alembic

# Aplicar migrações existentes
uv run alembic upgrade head

# Verificar status
uv run alembic current
```

---

## 🏃 Executando o Projeto

### Modo Desenvolvimento (Recomendado)

```bash
# Usando uvicorn diretamente
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Acessar Documentação

Após iniciar o servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Info**: http://localhost:8000/info

---

## 📁 Estrutura do Código

### Visão Geral (Clean Architecture)

```
src/
├── domain/              # 🎯 Camada de Domínio (regras de negócio)
│   ├── models/          # Entidades de domínio
│   ├── services/        # Serviços de domínio
│   └── exceptions.py    # Exceções customizadas
│
├── application/         # 📋 Camada de Aplicação (casos de uso)
│   ├── transaction_service.py
│   ├── painel_service.py
│   └── ...
│
├── ports/               # 🔌 Interfaces (contratos)
│   ├── transaction_port.py
│   └── ...
│
├── adapters/            # 🔧 Implementações de Infraestrutura
│   ├── controllers/     # HTTP endpoints (FastAPI)
│   ├── repositories/    # Acesso a dados (SQLAlchemy)
│   ├── presenters/      # Formatação de respostas
│   └── middlewares/     # Middlewares (auth, CORS, etc)
│
├── core/                # ⚙️ Configurações
│   ├── config.py        # Settings do projeto
│   └── schemas_api.py   # Schemas Pydantic para API
│
├── db/                  # 💾 Database
│   └── session.py       # Factory de sessões
│
├── shared/              # 🤝 Utilitários compartilhados
│   └── responses.py     # Helpers de resposta
│
└── main.py              # 🚪 Ponto de entrada
```

### Fluxo de Requisição

```
HTTP Request
    ↓
Controller (FastAPI)
    ↓
Application Service (caso de uso)
    ↓
Port (interface)
    ↓
Repository (implementação)
    ↓
Database
```

---

## ➕ Criando Novos Endpoints

### Passo a Passo Completo

#### 1. Criar Entidade de Domínio

```python
# src/domain/models/produto.py

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Produto:
    """Entidade de domínio: Produto"""

    id: Optional[int]
    nome: str
    preco: Decimal
    categoria: str

    def __post_init__(self):
        """Validações de domínio"""
        if self.preco <= 0:
            raise ValueError("Preço deve ser positivo")

        if not self.nome or len(self.nome) < 3:
            raise ValueError("Nome deve ter ao menos 3 caracteres")
```

#### 2. Criar Port (Interface)

```python
# src/ports/produto_port.py

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.produto import Produto

class IProdutoRepository(ABC):
    """Interface para repositório de produtos"""

    @abstractmethod
    async def create(self, produto: Produto) -> Produto:
        pass

    @abstractmethod
    async def get_by_id(self, produto_id: int) -> Optional[Produto]:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 10, offset: int = 0) -> List[Produto]:
        pass

    @abstractmethod
    async def update(self, produto_id: int, produto: Produto) -> Optional[Produto]:
        pass

    @abstractmethod
    async def delete(self, produto_id: int) -> bool:
        pass
```

#### 3. Criar Model ORM

```python
# src/adapters/repositories/models.py (adicionar)

class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    preco = Column(Numeric(10, 2), nullable=False)
    categoria = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

#### 4. Criar Repository

```python
# src/adapters/repositories/produto_repository.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.ports.produto_port import IProdutoRepository
from src.domain.models.produto import Produto
from src.adapters.repositories.models import ProdutoModel

class ProdutoRepository(IProdutoRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ProdutoModel) -> Produto:
        return Produto(
            id=model.id,
            nome=model.nome,
            preco=model.preco,
            categoria=model.categoria
        )

    def _to_model(self, produto: Produto) -> ProdutoModel:
        return ProdutoModel(
            id=produto.id,
            nome=produto.nome,
            preco=produto.preco,
            categoria=produto.categoria
        )

    async def create(self, produto: Produto) -> Produto:
        model = self._to_model(produto)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, produto_id: int) -> Optional[Produto]:
        stmt = select(ProdutoModel).where(ProdutoModel.id == produto_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
```

#### 5. Criar Application Service

```python
# src/application/produto_service.py

from typing import List
from src.ports.produto_port import IProdutoRepository
from src.domain.models.produto import Produto

class ProdutoService:

    def __init__(self, repository: IProdutoRepository):
        self.repository = repository

    async def create_produto(self, produto: Produto) -> Produto:
        # Validação já ocorre no __post_init__ da entidade
        return await self.repository.create(produto)

    async def get_produto(self, produto_id: int) -> Produto:
        produto = await self.repository.get_by_id(produto_id)
        if not produto:
            raise ValueError(f"Produto {produto_id} não encontrado")
        return produto

    async def list_produtos(self, limit: int = 10, offset: int = 0) -> List[Produto]:
        return await self.repository.list_all(limit, offset)
```

#### 6. Criar Schemas Pydantic

```python
# src/core/schemas_api.py (adicionar)

from pydantic import BaseModel, Field
from decimal import Decimal

class ProdutoCreateRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    preco: Decimal = Field(..., gt=0)
    categoria: str = Field(..., min_length=1, max_length=100)

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: Decimal
    categoria: str

    class Config:
        from_attributes = True
```

#### 7. Criar Presenter

```python
# src/adapters/presenters/produto_presenter.py

from src.domain.models.produto import Produto
from src.shared.responses import success_response

def present_produto(produto: Produto) -> dict:
    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco": float(produto.preco),
        "categoria": produto.categoria
    }

def present_produto_created(produto: Produto) -> dict:
    return success_response(
        code="PRODUTO_CREATED",
        message="Produto criado com sucesso",
        data=present_produto(produto)
    )
```

#### 8. Criar Controller

```python
# src/adapters/controllers/produto_controller.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.adapters.repositories.produto_repository import ProdutoRepository
from src.application.produto_service import ProdutoService
from src.adapters.presenters.produto_presenter import present_produto_created
from src.core.schemas_api import ProdutoCreateRequest
from src.domain.models.produto import Produto

router = APIRouter(tags=["Produtos"])

@router.post("/produtos", status_code=status.HTTP_201_CREATED)
async def create_produto(
    request: ProdutoCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo produto"""

    # Converter request para entidade
    produto = Produto(
        id=None,
        nome=request.nome,
        preco=request.preco,
        categoria=request.categoria
    )

    # Executar caso de uso
    repository = ProdutoRepository(session)
    service = ProdutoService(repository)
    created = await service.create_produto(produto)

    return present_produto_created(created)
```

#### 9. Registrar Router

```python
# src/main.py

from src.adapters.controllers.produto_controller import router as produto_router

app.include_router(produto_router, prefix="/api/v1", tags=["Produtos"])
```

#### 10. Criar Migration

```bash
# Gerar migration
uv run alembic revision --autogenerate -m "add_produtos_table"

# Aplicar
uv run alembic upgrade head
```

---

## 💾 Trabalhando com Banco de Dados

### Criar Nova Migration

```bash
# Autogenerate (detecta mudanças nos models)
uv run alembic revision --autogenerate -m "descrição_da_mudança"

# Manual (mais controle)
uv run alembic revision -m "descrição_da_mudança"
```

### Aplicar Migrations

```bash
# Aplicar todas pendentes
uv run alembic upgrade head

# Aplicar específica
uv run alembic upgrade <revision_id>

# Aplicar próxima
uv run alembic upgrade +1
```

### Reverter Migrations

```bash
# Reverter última
uv run alembic downgrade -1

# Reverter específica
uv run alembic downgrade <revision_id>

# Reverter todas
uv run alembic downgrade base
```

### Histórico de Migrations

```bash
# Ver histórico
uv run alembic history

# Ver migration atual
uv run alembic current

# Ver SQL que será executado (sem aplicar)
uv run alembic upgrade head --sql
```

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
uv run pytest

# Com cobertura
uv run pytest --cov=src --cov-report=html

# Testes específicos
uv run pytest tests/unit/test_transaction.py

# Verbose
uv run pytest -v

# Parar no primeiro erro
uv run pytest -x

# Ver print statements
uv run pytest -s
```

### Estrutura de Testes

```
tests/
├── unit/                # Testes unitários
│   ├── domain/          # Testes de entidades
│   ├── application/     # Testes de services
│   └── adapters/        # Testes de repositories
│
├── integration/         # Testes de integração
│   └── test_api.py      # Testes de endpoints
│
└── conftest.py          # Fixtures compartilhadas
```

### Exemplo de Teste

```python
# tests/unit/domain/test_produto.py

import pytest
from decimal import Decimal
from src.domain.models.produto import Produto

def test_produto_valido():
    produto = Produto(
        id=None,
        nome="Produto Teste",
        preco=Decimal("10.50"),
        categoria="Eletrônicos"
    )
    assert produto.nome == "Produto Teste"
    assert produto.preco == Decimal("10.50")

def test_produto_preco_invalido():
    with pytest.raises(ValueError, match="Preço deve ser positivo"):
        Produto(
            id=None,
            nome="Teste",
            preco=Decimal("-5.00"),
            categoria="Teste"
        )
```

---

## ✅ Boas Práticas

### Código

1. **Siga Clean Architecture**: Nunca importe `adapters` no `domain`
2. **Use Type Hints**: Sempre anote tipos
3. **Docstrings**: Documente funções públicas
4. **Validações**: Coloque validações de negócio no domain
5. **Async/Await**: Use async em operações de I/O

### Commits

```bash
# Padrão de mensagem
<tipo>: <descrição curta>

<corpo opcional>

# Tipos:
feat: Nova funcionalidade
fix: Correção de bug
refactor: Refatoração de código
docs: Documentação
test: Testes
chore: Tarefas de manutenção
```

### Exemplo:

```
feat: adicionar endpoint de criação de produtos

- Criar entidade Produto
- Implementar repository
- Adicionar controller com POST /produtos
- Adicionar testes unitários
```

---

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**
```bash
# Reinstale dependências
uv sync

# Execute com uv run
uv run uvicorn src.main:app --reload
```

### Erro: "Table doesn't exist"

**Solução:**
```bash
# Verifique migrations
uv run alembic current

# Aplique migrations
uv run alembic upgrade head
```

### Erro: "Database is locked"

**Solução (SQLite):**
```bash
# Pare o servidor
# Delete conexões antigas
rm home_finance.db-wal home_finance.db-shm

# Reinicie
```

### Servidor não recarrega automaticamente

**Solução:**
```bash
# Use --reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Erro 422 Unprocessable Entity

**Causa:** Validação Pydantic falhou

**Solução:** Verifique o corpo da requisição contra o schema esperado

---

## 📚 Recursos Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Clean Architecture Guide](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Última Atualização:** 2025-10-22
**Versão do Projeto:** 0.1.0
