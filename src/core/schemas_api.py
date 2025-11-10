"""
API Schemas
Schemas Pydantic específicos para requisições da API
Separados dos schemas de domínio
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ===== SCHEMAS DE RESPOSTA =====

class BaseResponse(BaseModel):
    """Schema base para todas as respostas da API"""
    code: str = Field(..., description="Código da resposta")
    message: str = Field(..., description="Mensagem da resposta")
    data: Any | None = Field(None, description="Dados da resposta")


class TransactionResponse(BaseModel):
    """Schema de resposta para uma transação"""
    id: int = Field(..., description="ID da transação")
    data: str = Field(..., description="Data da transação (ISO format)")
    descricao: str = Field(..., description="Descrição da transação")
    valor: float = Field(..., description="Valor da transação")
    tipo: str = Field(..., description="Tipo: ENTRADA ou SAIDA")
    categoria: str = Field(..., description="Categoria da transação")
    recorrencia: str | None = Field(None, description="Recorrência")
    parcelas: int | None = Field(None, description="Número de parcelas")
    tipo_divisao: str = Field(..., description="Tipo de divisão")
    valor_por_pessoa: float | None = Field(None, description="Valor por pessoa")
    porcentagem_divisao: int | None = Field(None, description="Porcentagem de divisão")
    local_id: int | None = Field(None, description="ID do local")
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
    data: list[TransactionResponse] = Field(..., description="Lista de transações")


class TransactionUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de transação"""
    data: TransactionResponse = Field(..., description="Dados da transação atualizada")


class TransactionDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de transação"""
    data: None = Field(None, description="Dados da resposta (null para exclusão)")


class LocalResponse(BaseModel):
    """Schema de resposta para um local"""
    id: int = Field(..., description="ID do local")
    nome_fantasia: str | None = Field(None, description="Nome fantasia")
    cnpj: str | None = Field(None, description="CNPJ")
    razao_social: str | None = Field(None, description="Razão social")
    categoria: str | None = Field(None, description="Categoria")
    endereco: str | None = Field(None, description="Endereço")
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
    data: list[LocalResponse] = Field(..., description="Lista de locais")


class LocalUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de local"""
    data: LocalResponse = Field(..., description="Dados do local atualizado")


class LocalDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de local"""
    data: None = Field(None, description="Dados da resposta (null para exclusão)")


class UsuarioResponse(BaseModel):
    """Schema de resposta para um usuário"""
    id: int = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    email: str | None = Field(None, description="Email do usuário")
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
    data: list[UsuarioResponse] = Field(..., description="Lista de usuários")


class UsuarioUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de usuário"""
    data: UsuarioResponse = Field(..., description="Dados do usuário atualizado")


class UsuarioDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de usuário"""
    data: None = Field(None, description="Dados da resposta (null para exclusão)")


class PainelResponse(BaseModel):
    """Schema de resposta para um painel"""
    id: int = Field(..., description="ID do painel")
    nome: str = Field(..., description="Nome do painel")
    descricao: str | None = Field(None, description="Descrição do painel")
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
    data: list[PainelResponse] = Field(..., description="Lista de painéis")


class PainelUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de painel"""
    data: PainelResponse = Field(..., description="Dados do painel atualizado")


class PainelDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de painel"""
    data: None = Field(None, description="Dados da resposta (null para exclusão)")


# ===== SCHEMAS DE CATEGORIA =====

class CategoriaResponse(BaseModel):
    """Schema de resposta para uma categoria"""
    id: int = Field(..., description="ID da categoria")
    nome: str = Field(..., description="Nome da categoria")
    descricao: str | None = Field(None, description="Descrição da categoria")
    usuario_id: int | None = Field(None, description="ID do usuário proprietário (null para categorias padrão)")
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
    data: list[CategoriaResponse] = Field(..., description="Lista de categorias")


class CategoriaUpdateResponse(BaseResponse):
    """Schema de resposta para atualização de categoria"""
    data: CategoriaResponse = Field(..., description="Dados da categoria atualizada")


class CategoriaDeleteResponse(BaseResponse):
    """Schema de resposta para exclusão de categoria"""
    data: None = Field(None, description="Dados da resposta (null para exclusão)")


# ===== SCHEMAS DE REQUEST =====


class TransactionCreateRequest(BaseModel):
    """Schema para criar transação via API"""
    data: date = Field(..., description="Data da transação")
    descricao: str = Field(..., min_length=1, max_length=255, description="Descrição")
    valor: Decimal = Field(..., gt=0, description="Valor da transação")
    tipo: str = Field(..., pattern="^(ENTRADA|SAIDA)$", description="Tipo: ENTRADA ou SAIDA")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoria")
    recorrencia: str | None = Field(
        None,
        pattern="^(DIARIO|SEMANAL|MENSAL|OCASIONAL)$",
        description="Recorrência"
    )
    parcelas: int | None = Field(None, gt=0, description="Número de parcelas")
    tipo_divisao: str | None = Field(
        "PESSOAL",
        pattern="^(PESSOAL|COMPARTILHADO_50_50|COMPARTILHADO_CUSTOM)$",
        description="Tipo de divisão: PESSOAL, COMPARTILHADO_50_50 ou COMPARTILHADO_CUSTOM"
    )
    valor_por_pessoa: Decimal | None = Field(None, ge=0, description="Valor que cada pessoa paga")
    porcentagem_divisao: int | None = Field(None, ge=1, le=100, description="Porcentagem para divisão customizada (1-100)")
    local_id: int | None = Field(None, description="ID do local")
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
    data: date | None = None
    descricao: str | None = Field(None, min_length=1, max_length=255)
    valor: Decimal | None = Field(None, gt=0)
    tipo: str | None = Field(None, pattern="^(ENTRADA|SAIDA)$")
    categoria: str | None = Field(None, min_length=1, max_length=100)
    recorrencia: str | None = Field(None, pattern="^(DIARIO|SEMANAL|MENSAL|OCASIONAL)$")
    parcelas: int | None = Field(None, gt=0)
    tipo_divisao: str | None = Field(
        None,
        pattern="^(PESSOAL|COMPARTILHADO_50_50|COMPARTILHADO_CUSTOM)$",
        description="Tipo de divisão"
    )
    valor_por_pessoa: Decimal | None = Field(None, ge=0, description="Valor por pessoa")
    porcentagem_divisao: int | None = Field(None, ge=1, le=100, description="Porcentagem de divisão")
    local_id: int | None = None
    painel_id: int | None = None


class LocalCreateRequest(BaseModel):
    """Schema para criar local via API"""
    nome_fantasia: str | None = Field(None, max_length=255)
    cnpj: str | None = Field(None, max_length=18)
    razao_social: str | None = Field(None, max_length=255)
    categoria: str | None = Field(None, max_length=100)
    endereco: str | None = None


class LocalUpdateRequest(BaseModel):
    """Schema para atualizar local via API"""
    nome_fantasia: str | None = Field(None, max_length=255)
    cnpj: str | None = Field(None, max_length=18)
    razao_social: str | None = Field(None, max_length=255)
    categoria: str | None = Field(None, max_length=100)
    endereco: str | None = None


class UsuarioCreateRequest(BaseModel):
    """Schema para criar usuário via API"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do usuário")
    email: str | None = Field(None, max_length=255, description="Email do usuário")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None and v.strip():
            if '@' not in v or '.' not in v.split('@')[-1]:
                raise ValueError('Email inválido')
        return v


class UsuarioUpdateRequest(BaseModel):
    """Schema para atualizar usuário via API"""
    nome: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, max_length=255)


class PainelCreateRequest(BaseModel):
    """Schema para criar painel via API"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do painel")
    descricao: str | None = Field(None, max_length=1000, description="Descrição do painel")
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
    nome: str | None = Field(None, min_length=1, max_length=255)
    descricao: str | None = Field(None, max_length=1000)
    tipo_conta: str | None = Field(
        None,
        pattern="^(CARTAO_CREDITO|CONTA_BANCARIA|DINHEIRO)$",
        description="Tipo de conta"
    )


class CategoriaCreateRequest(BaseModel):
    """Schema para criar categoria via API"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: str | None = Field(None, max_length=500, description="Descrição da categoria")


class CategoriaUpdateRequest(BaseModel):
    """Schema para atualizar categoria via API"""
    nome: str | None = Field(None, min_length=1, max_length=100, description="Nome da categoria")
    descricao: str | None = Field(None, max_length=500, description="Descrição da categoria")


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
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    total_entradas: Decimal = Field(..., description="Total de entradas")
    total_saidas: Decimal = Field(..., description="Total de saídas")
    saldo: Decimal = Field(..., description="Saldo (entradas - saídas)")
    quantidade_transacoes: int = Field(..., description="Número total de transações")


class TransactionFilters(BaseModel):
    """Schema para filtros de transações"""
    painel_id: int = Field(..., description="ID do painel (obrigatório)")
    data_inicio: date | None = Field(None, description="Data inicial do filtro")
    data_fim: date | None = Field(None, description="Data final do filtro")
    tipo: str | None = Field(None, pattern="^(ENTRADA|SAIDA)$", description="Tipo de transação")
    categoria: str | None = Field(None, description="Categoria")
    local_id: int | None = Field(None, description="ID do local")
    page: int = Field(1, ge=1, description="Número da página")
    page_size: int = Field(50, ge=1, le=100, description="Tamanho da página")


# ===== AUTH SCHEMAS =====

class RegisterRequest(BaseModel):
    """Schema para registro de novo usuário"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do usuário")
    email: str = Field(..., min_length=3, max_length=255, description="Email do usuário")
    password: str = Field(..., min_length=8, max_length=128, description="Senha do usuário")


class LoginRequest(BaseModel):
    """Schema para login de usuário"""
    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class AuthUserResponse(BaseModel):
    """Schema de resposta com dados do usuário autenticado"""
    id: int = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")


class AuthDataResponse(BaseModel):
    """Schema de dados de autenticação (com token no body - deprecated)"""
    user: AuthUserResponse = Field(..., description="Dados do usuário")
    token: str = Field(..., description="Token JWT de autenticação")


class AuthDataResponseCookie(BaseModel):
    """Schema de dados de autenticação (token via HttpOnly cookie)"""
    user: AuthUserResponse = Field(..., description="Dados do usuário")


class AuthResponse(BaseResponse):
    """Schema de resposta para login/registro bem-sucedido (com token no body - deprecated)"""
    data: AuthDataResponse = Field(..., description="Dados de autenticação")


class AuthResponseCookie(BaseResponse):
    """Schema de resposta para login/registro bem-sucedido (token via HttpOnly cookie)"""
    data: AuthDataResponseCookie = Field(..., description="Dados do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "AUTH_SUCCESS",
                "message": "Autenticação realizada com sucesso",
                "data": {
                    "user": {
                        "id": 1,
                        "nome": "João Silva",
                        "email": "joao@example.com"
                    }
                }
            }
        }


# ===== SESSION RECOVERY SCHEMAS =====

class SessionInfo(BaseModel):
    """Informações da sessão do usuário"""
    valid: bool = Field(..., description="Se a sessão é válida")
    expires_at: str | None = Field(None, description="Data de expiração do token (ISO 8601)")
    issued_at: str | None = Field(None, description="Data de emissão do token (ISO 8601)")


class UserSessionData(BaseModel):
    """Dados completos do usuário com informações de sessão"""
    id: int = Field(..., description="ID do usuário")
    nome: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    criado_em: str | None = Field(None, description="Data de criação (ISO 8601)")


class SessionRecoveryData(BaseModel):
    """Schema de dados para recuperação de sessão"""
    user: UserSessionData = Field(..., description="Dados do usuário")
    session: SessionInfo = Field(..., description="Informações da sessão")


class SessionRecoveryResponse(BaseResponse):
    """Schema de resposta para recuperação de sessão (/auth/me)"""
    data: SessionRecoveryData = Field(..., description="Dados do usuário e sessão")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "SESSION_VALID",
                "message": "Sessão recuperada com sucesso",
                "data": {
                    "user": {
                        "id": 1,
                        "nome": "João Silva",
                        "email": "joao@example.com",
                        "criado_em": "2025-01-01T00:00:00Z"
                    },
                    "session": {
                        "valid": True,
                        "expires_at": "2025-11-10T14:00:00Z",
                        "issued_at": "2025-11-10T13:30:00Z"
                    }
                }
            }
        }
