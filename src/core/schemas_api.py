"""
API Schemas
Schemas Pydantic específicos para requisições da API
Separados dos schemas de domínio
"""

from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List, Any


# ===== SCHEMAS DE RESPOSTA =====

class BaseResponse(BaseModel):
    """Schema base para todas as respostas da API"""
    code: str = Field(..., description="Código da resposta")
    message: str = Field(..., description="Mensagem da resposta")
    data: Optional[Any] = Field(None, description="Dados da resposta")


class TransactionResponse(BaseModel):
    """Schema de resposta para uma transação"""
    id: int = Field(..., description="ID da transação")
    data: str = Field(..., description="Data da transação (ISO format)")
    descricao: str = Field(..., description="Descrição da transação")
    valor: float = Field(..., description="Valor da transação")
    tipo: str = Field(..., description="Tipo: ENTRADA ou SAIDA")
    categoria: str = Field(..., description="Categoria da transação")
    recorrencia: Optional[str] = Field(None, description="Recorrência")
    parcelas: Optional[int] = Field(None, description="Número de parcelas")
    tipo_divisao: str = Field(..., description="Tipo de divisão")
    valor_por_pessoa: Optional[float] = Field(None, description="Valor por pessoa")
    porcentagem_divisao: Optional[int] = Field(None, description="Porcentagem de divisão")
    local_id: Optional[int] = Field(None, description="ID do local")
    painel_id: int = Field(..., description="ID do painel")
    criado_em: str = Field(..., description="Data de criação (ISO format)")
    atualizado_em: str = Field(..., description="Data de atualização (ISO format)")


class TransactionCreateResponse(BaseResponse):
    """Schema de resposta para criação de transação"""
    data: TransactionResponse = Field(..., description="Dados da transação criada")


class TransactionDetailResponse(BaseResponse):
    """Schema de resposta para detalhe de transação"""
    data: TransactionResponse = Field(..., description="Dados da transação")


class TransactionListResponse(BaseResponse):
    """Schema de resposta para lista de transações"""
    data: List[TransactionResponse] = Field(..., description="Lista de transações")


class TransactionUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de transação"""
    data: TransactionResponse = Field(..., description="Dados da transação atualizada")


class TransactionDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de transação"""
    data: Optional[None] = Field(None, description="Dados da resposta (null para exclusão)")


class LocalResponse(BaseModel):
    """Schema de resposta para um local"""
    id: int = Field(..., description="ID do local")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia")
    cnpj: Optional[str] = Field(None, description="CNPJ")
    razao_social: Optional[str] = Field(None, description="Razão social")
    categoria: Optional[str] = Field(None, description="Categoria")
    endereco: Optional[str] = Field(None, description="Endereço")
    criado_em: str = Field(..., description="Data de criação (ISO format)")
    atualizado_em: str = Field(..., description="Data de atualização (ISO format)")


class LocalCreateResponse(BaseResponse):
    """Schema de resposta para criação de local"""
    data: LocalResponse = Field(..., description="Dados do local criado")


class LocalDetailResponse(BaseResponse):
    """Schema de resposta para detalhe de local"""
    data: LocalResponse = Field(..., description="Dados do local")


class LocalListResponse(BaseResponse):
    """Schema de resposta para lista de locais"""
    data: List[LocalResponse] = Field(..., description="Lista de locais")


class LocalUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de local"""
    data: LocalResponse = Field(..., description="Dados do local atualizado")


class LocalDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de local"""
    data: Optional[None] = Field(None, description="Dados da resposta (null para exclusão)")


class UsuarioResponse(BaseModel):
    """Schema de resposta para um usuário"""
    id: int = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    email: Optional[str] = Field(None, description="Email do usuário")
    criado_em: str = Field(..., description="Data de criação (ISO format)")
    atualizado_em: str = Field(..., description="Data de atualização (ISO format)")


class UsuarioCreateResponse(BaseResponse):
    """Schema de resposta para criação de usuário"""
    data: UsuarioResponse = Field(..., description="Dados do usuário criado")


class UsuarioDetailResponse(BaseResponse):
    """Schema de resposta para detalhe de usuário"""
    data: UsuarioResponse = Field(..., description="Dados do usuário")


class UsuarioListResponse(BaseResponse):
    """Schema de resposta para lista de usuários"""
    data: List[UsuarioResponse] = Field(..., description="Lista de usuários")


class UsuarioUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de usuário"""
    data: UsuarioResponse = Field(..., description="Dados do usuário atualizado")


class UsuarioDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de usuário"""
    data: Optional[None] = Field(None, description="Dados da resposta (null para exclusão)")


class PainelResponse(BaseModel):
    """Schema de resposta para um painel"""
    id: int = Field(..., description="ID do painel")
    nome: str = Field(..., description="Nome do painel")
    descricao: Optional[str] = Field(None, description="Descrição do painel")
    tipo_conta: str = Field(..., description="Tipo de conta")
    usuario_id: int = Field(..., description="ID do usuário proprietário")
    criado_em: str = Field(..., description="Data de criação (ISO format)")
    atualizado_em: str = Field(..., description="Data de atualização (ISO format)")


class PainelCreateResponse(BaseResponse):
    """Schema de resposta para criação de painel"""
    data: PainelResponse = Field(..., description="Dados do painel criado")


class PainelDetailResponse(BaseResponse):
    """Schema de resposta para detalhe de painel"""
    data: PainelResponse = Field(..., description="Dados do painel")


class PainelListResponse(BaseResponse):
    """Schema de resposta para lista de painéis"""
    data: List[PainelResponse] = Field(..., description="Lista de painéis")


class PainelUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de painel"""
    data: PainelResponse = Field(..., description="Dados do painel atualizado")


class PainelDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de painel"""
    data: Optional[None] = Field(None, description="Dados da resposta (null para exclusão)")


# ===== SCHEMAS DE CATEGORIA =====

class CategoriaResponse(BaseModel):
    """Schema de resposta para uma categoria"""
    id: int = Field(..., description="ID da categoria")
    nome: str = Field(..., description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")
    usuario_id: Optional[int] = Field(None, description="ID do usuário proprietário (null para categorias padrão)")
    is_default: bool = Field(..., description="Indica se é categoria padrão do sistema")
    criado_em: str = Field(..., description="Data de criação (ISO format)")
    atualizado_em: str = Field(..., description="Data de atualização (ISO format)")


class CategoriaCreateResponse(BaseResponse):
    """Schema de resposta para criação de categoria"""
    data: CategoriaResponse = Field(..., description="Dados da categoria criada")


class CategoriaDetailResponse(BaseResponse):
    """Schema de resposta para detalhe de categoria"""
    data: CategoriaResponse = Field(..., description="Dados da categoria")


class CategoriaListResponse(BaseResponse):
    """Schema de resposta para lista de categorias"""
    data: List[CategoriaResponse] = Field(..., description="Lista de categorias")


class CategoriaUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de categoria"""
    data: CategoriaResponse = Field(..., description="Dados da categoria atualizada")


class CategoriaDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de categoria"""
    data: Optional[None] = Field(None, description="Dados da resposta (null para exclusão)")


# ===== SCHEMAS DE REQUEST =====


class TransactionCreateRequest(BaseModel):
    """Schema para criar transação via API"""
    data: date = Field(..., description="Data da transação")
    descricao: str = Field(..., min_length=1, max_length=255, description="Descrição")
    valor: Decimal = Field(..., gt=0, description="Valor da transação")
    tipo: str = Field(..., pattern="^(ENTRADA|SAIDA)$", description="Tipo: ENTRADA ou SAIDA")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoria")
    recorrencia: Optional[str] = Field(
        None,
        pattern="^(DIARIO|SEMANAL|MENSAL|OCASIONAL)$",
        description="Recorrência"
    )
    parcelas: Optional[int] = Field(None, gt=0, description="Número de parcelas")
    tipo_divisao: Optional[str] = Field(
        "PESSOAL",
        pattern="^(PESSOAL|COMPARTILHADO_50_50|COMPARTILHADO_CUSTOM)$",
        description="Tipo de divisão: PESSOAL, COMPARTILHADO_50_50 ou COMPARTILHADO_CUSTOM"
    )
    valor_por_pessoa: Optional[Decimal] = Field(None, ge=0, description="Valor que cada pessoa paga")
    porcentagem_divisao: Optional[int] = Field(None, ge=1, le=100, description="Porcentagem para divisão customizada (1-100)")
    local_id: Optional[int] = Field(None, description="ID do local")
    painel_id: int = Field(..., description="ID do painel")

    @field_validator('tipo_divisao', mode='after')
    @classmethod
    def validate_tipo_divisao(cls, v, info):
        """Valida que tipo_divisao tem valores corretos"""
        if v and v not in ['PESSOAL', 'COMPARTILHADO_50_50', 'COMPARTILHADO_CUSTOM']:
            raise ValueError('tipo_divisao deve ser PESSOAL, COMPARTILHADO_50_50 ou COMPARTILHADO_CUSTOM')
        return v or 'PESSOAL'

    @field_validator('porcentagem_divisao', mode='after')
    @classmethod
    def validate_porcentagem(cls, v, info):
        """Valida porcentagem_divisao quando tipo_divisao é COMPARTILHADO_CUSTOM"""
        values = info.data
        tipo_divisao = values.get('tipo_divisao')

        if tipo_divisao == 'COMPARTILHADO_CUSTOM':
            if v is None:
                raise ValueError('porcentagem_divisao é obrigatório quando tipo_divisao é COMPARTILHADO_CUSTOM')
            if v <= 0 or v > 100:
                raise ValueError('porcentagem_divisao deve estar entre 1 e 100')

        return v


class TransactionUpdateRequest(BaseModel):
    """Schema para atualizar transação via API"""
    data: Optional[date] = None
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0)
    tipo: Optional[str] = Field(None, pattern="^(ENTRADA|SAIDA)$")
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    recorrencia: Optional[str] = Field(None, pattern="^(DIARIO|SEMANAL|MENSAL|OCASIONAL)$")
    parcelas: Optional[int] = Field(None, gt=0)
    tipo_divisao: Optional[str] = Field(
        None,
        pattern="^(PESSOAL|COMPARTILHADO_50_50|COMPARTILHADO_CUSTOM)$",
        description="Tipo de divisão"
    )
    valor_por_pessoa: Optional[Decimal] = Field(None, ge=0, description="Valor por pessoa")
    porcentagem_divisao: Optional[int] = Field(None, ge=1, le=100, description="Porcentagem de divisão")
    local_id: Optional[int] = None
    painel_id: Optional[int] = None


class LocalCreateRequest(BaseModel):
    """Schema para criar local via API"""
    nome_fantasia: Optional[str] = Field(None, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    razao_social: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = None


class LocalUpdateRequest(BaseModel):
    """Schema para atualizar local via API"""
    nome_fantasia: Optional[str] = Field(None, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    razao_social: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = None


class UsuarioCreateRequest(BaseModel):
    """Schema para criar usuário via API"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do usuário")
    email: Optional[str] = Field(None, max_length=255, description="Email do usuário")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None and v.strip():
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Email inválido')
        return v


class UsuarioUpdateRequest(BaseModel):
    """Schema para atualizar usuário via API"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)


class PainelCreateRequest(BaseModel):
    """Schema para criar painel via API"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do painel")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do painel")
    tipo_conta: str = Field(
        ...,
        pattern="^(CARTAO_CREDITO|CONTA_BANCARIA|DINHEIRO)$",
        description="Tipo de conta: CARTAO_CREDITO, CONTA_BANCARIA ou DINHEIRO"
    )
    usuario_id: int = Field(..., gt=0, description="ID do usuário proprietário")

    @field_validator('tipo_conta')
    @classmethod
    def validate_tipo_conta(cls, v):
        """Valida que tipo_conta tem valores corretos"""
        if v not in ['CARTAO_CREDITO', 'CONTA_BANCARIA', 'DINHEIRO']:
            raise ValueError('tipo_conta deve ser CARTAO_CREDITO, CONTA_BANCARIA ou DINHEIRO')
        return v


class PainelUpdateRequest(BaseModel):
    """Schema para atualizar painel via API"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    tipo_conta: Optional[str] = Field(
        None,
        pattern="^(CARTAO_CREDITO|CONTA_BANCARIA|DINHEIRO)$",
        description="Tipo de conta"
    )


class CategoriaCreateRequest(BaseModel):
    """Schema para criar categoria via API"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição da categoria")


class CategoriaUpdateRequest(BaseModel):
    """Schema para atualizar categoria via API"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição da categoria")


class CompartilhamentoPainelRequest(BaseModel):
    """Schema para compartilhar painel"""
    usuario_id: int = Field(..., gt=0, description="ID do usuário para compartilhar")
    tipo_permissao: str = Field(
        ...,
        pattern="^(OWNER|EDITOR|VIEWER)$",
        description="Tipo de permissão: OWNER, EDITOR ou VIEWER"
    )


class CompartilhamentoPainelUpdateRequest(BaseModel):
    """Schema para atualizar permissão de compartilhamento"""
    tipo_permissao: str = Field(
        ...,
        pattern="^(OWNER|EDITOR|VIEWER)$",
        description="Tipo de permissão: OWNER, EDITOR ou VIEWER"
    )


class CompartilhamentoPainelResponse(BaseModel):
    """Schema de resposta para compartilhamento"""
    id: int
    painel_id: int
    usuario_id: int
    tipo_permissao: str
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class BalancoResponse(BaseModel):
    """Schema de resposta para balanço do painel"""
    painel_id: int
    nome_painel: str
    periodo_inicio: Optional[date] = None
    periodo_fim: Optional[date] = None
    total_entradas: Decimal = Field(..., description="Total de entradas")
    total_saidas: Decimal = Field(..., description="Total de saídas")
    saldo: Decimal = Field(..., description="Saldo (entradas - saídas)")
    quantidade_transacoes: int = Field(..., description="Número total de transações")


class TransactionFilters(BaseModel):
    """Schema para filtros de transações"""
    painel_id: int = Field(..., description="ID do painel (obrigatório)")
    data_inicio: Optional[date] = Field(None, description="Data inicial do filtro")
    data_fim: Optional[date] = Field(None, description="Data final do filtro")
    tipo: Optional[str] = Field(None, pattern="^(ENTRADA|SAIDA)$", description="Tipo de transação")
    categoria: Optional[str] = Field(None, description="Categoria")
    local_id: Optional[int] = Field(None, description="ID do local")
    page: int = Field(1, ge=1, description="Número da página")
    page_size: int = Field(50, ge=1, le=100, description="Tamanho da página")
