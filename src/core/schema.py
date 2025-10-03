"""
Configuração de schemas e estruturas de dados padronizadas
"""

from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    """Tipos de transação financeira"""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    """Status da transação"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AccountType(str, Enum):
    """Tipos de conta"""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    CASH = "cash"


class Currency(str, Enum):
    """Moedas suportadas"""
    USD = "USD"
    EUR = "EUR"
    BRL = "BRL"


class TransactionBase(BaseModel):
    """Schema base para transações"""
    amount: Decimal = Field(..., gt=0, description="Valor da transação")
    description: str = Field(..., min_length=1, max_length=255, description="Descrição da transação")
    transaction_type: TransactionType = Field(..., description="Tipo da transação")
    transaction_date: date = Field(default_factory=date.today, description="Data da transação")
    category: Optional[str] = Field(None, max_length=100, description="Categoria da transação")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags da transação")
    currency: Currency = Field(default=Currency.BRL, description="Moeda da transação")
    
    @validator("amount")
    def validate_amount(cls, v):
        """Valida o valor da transação"""
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v
    
    @validator("tags")
    def validate_tags(cls, v):
        """Valida as tags"""
        if v:
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class TransactionCreate(TransactionBase):
    """Schema para criação de transação"""
    account_id: int = Field(..., description="ID da conta")


class TransactionUpdate(BaseModel):
    """Schema para atualização de transação"""
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    transaction_type: Optional[TransactionType] = None
    transaction_date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    currency: Optional[Currency] = None
    status: Optional[TransactionStatus] = None


class TransactionResponse(TransactionBase):
    """Schema de resposta da transação"""
    id: int
    account_id: int
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    """Schema base para contas"""
    name: str = Field(..., min_length=1, max_length=100, description="Nome da conta")
    account_type: AccountType = Field(..., description="Tipo da conta")
    balance: Decimal = Field(default=Decimal("0.00"), description="Saldo da conta")
    currency: Currency = Field(default=Currency.BRL, description="Moeda da conta")
    is_active: bool = Field(default=True, description="Se a conta está ativa")


class AccountCreate(AccountBase):
    """Schema para criação de conta"""
    pass


class AccountUpdate(BaseModel):
    """Schema para atualização de conta"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    account_type: Optional[AccountType] = None
    currency: Optional[Currency] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    """Schema de resposta da conta"""
    id: int
    created_at:datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """Schema de resposta do healthcheck"""
    status: str = Field(..., description="Status do serviço")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da verificação")
    version: str = Field(..., description="Versão da aplicação")
    database_status: str = Field(..., description="Status do banco de dados")
    uptime_seconds: float = Field(..., description="Tempo de funcionamento em segundos")


# Schemas para paginação
class PaginationRequest(BaseModel):
    """Schema para requisições com paginação"""
    page: int = Field(default=1, ge=1, description="Número da página")
    size: int = Field(default=20, ge=1, le=100, description="Tamanho da página")
    
    @validator("page")
    def validate_page(cls, v):
        """Valida número da página"""
        if v < 1:
            raise ValueError("Página deve ser maior que 0")
        return v


class PaginationResponse(BaseModel):
    """Schema para respostas com paginação"""
    total: int = Field(..., description="Total de itens")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Se tem próxima página")
    has_prev: bool = Field(..., description="Se tem página anterior")


class TransactionListResponse(BaseModel):
    """Schema para lista de transações com paginação"""
    transactions: List[TransactionResponse]
    pagination: PaginationResponse


class TransactionListRequest(BaseModel):
    """Schema para filtros de busca de transações"""
    account_id: Optional[int] = None
    transaction_type: Optional[TransactionType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    search: Optional[str] = Field(None, description="Busca por texto na descrição")
    pagination: PaginationRequest = Field(default_factory=PaginationRequest)


# Schemas de erro
class ErrorDetail(BaseModel):
    """Detalhes de erro"""
    field: Optional[str] = None
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Schema de resposta de erro"""
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Schemas de sucesso
class SuccessResponse(BaseModel):
    """Schema de resposta de sucesso"""
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Schemas de estatísticas
class MonthlyOverviewResponse(BaseModel):
    """Schema para visão geral mensal"""
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    net_flow: Decimal
    transaction_count: int


class CategoryOverviewResponse(BaseModel):
    """Schema para visão geral por categoria"""
    category: str
    total_amount: Decimal
    transaction_count: int
    percentage: float
