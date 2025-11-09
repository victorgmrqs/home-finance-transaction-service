"""
Entidade de Domínio: Transaction
Representa uma transação financeira no sistema
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class TransactionType(str, Enum):
    """Tipos de transação financeira"""
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class Recurrence(str, Enum):
    """Tipos de recorrência de transação"""
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    MENSAL = "MENSAL"
    OCASIONAL = "OCASIONAL"


class TipoDivisao(str, Enum):
    """Tipos de divisão de gastos"""
    PESSOAL = "PESSOAL"
    COMPARTILHADO_50_50 = "COMPARTILHADO_50_50"
    COMPARTILHADO_CUSTOM = "COMPARTILHADO_CUSTOM"


@dataclass
class Transaction:
    """
    Entidade de domínio: Transação Financeira

    Representa uma movimentação financeira (entrada ou saída) no sistema.
    Contém as regras de negócio relacionadas a transações.

    Divisão de gastos:
    - PESSOAL: Gasto individual (padrão)
    - COMPARTILHADO_50_50: Dividido 50/50 entre duas pessoas
    - COMPARTILHADO_CUSTOM: Divisão personalizada com porcentagem

    Parcelamento:
    - parcelas: Número total de parcelas
    - parcela_numero: Número desta parcela (1, 2, 3...)
    - transacao_mae_id: ID da primeira parcela (null se for a parcela 1)
    - eh_parcela: True se faz parte de um parcelamento

    Recorrência:
    - recorrencia: Tipo de recorrência (DIARIO, SEMANAL, MENSAL, OCASIONAL)
    - transacao_recorrente_origem_id: ID da transação que gerou esta (se recorrente)
    - recorrencia_ativa: Se False, para de gerar novas recorrências
    - proxima_geracao: Próxima data em que deve gerar recorrência
    """
    id: int | None
    data: date
    descricao: str
    valor: Decimal
    tipo: TransactionType
    categoria: str
    painel_id: int
    recorrencia: Recurrence | None = None
    parcelas: int | None = None
    tipo_divisao: TipoDivisao = TipoDivisao.PESSOAL
    valor_por_pessoa: Decimal | None = None
    porcentagem_divisao: int | None = None
    local_id: int | None = None

    # Campos de parcelamento
    parcela_numero: int | None = None
    transacao_mae_id: int | None = None
    eh_parcela: bool = False

    # Campos de recorrência
    transacao_recorrente_origem_id: int | None = None
    recorrencia_ativa: bool = True
    proxima_geracao: date | None = None

    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    def __post_init__(self):
        """Valida a transação após inicialização"""
        self._validate()

    def _validate(self):
        """Valida regras de negócio da transação"""
        if self.valor <= 0:
            raise ValueError("Valor deve ser maior que zero")

        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descrição é obrigatória e não pode ser vazia")

        if len(self.descricao) > 255:
            raise ValueError("Descrição não pode ter mais de 255 caracteres")

        if self.parcelas is not None and self.parcelas < 1:
            raise ValueError("Número de parcelas deve ser maior que zero")

        if not self.categoria or not self.categoria.strip():
            raise ValueError("Categoria é obrigatória")

        if len(self.categoria) > 100:
            raise ValueError("Categoria não pode ter mais de 100 caracteres")

        if self.painel_id is None or self.painel_id <= 0:
            raise ValueError("ID do painel é obrigatório e deve ser maior que zero")

        # Validações de divisão de gastos
        if self.tipo_divisao == TipoDivisao.COMPARTILHADO_CUSTOM:
            if self.porcentagem_divisao is None:
                raise ValueError("porcentagem_divisao é obrigatória quando tipo_divisao é COMPARTILHADO_CUSTOM")
            if self.porcentagem_divisao <= 0 or self.porcentagem_divisao > 100:
                raise ValueError("porcentagem_divisao deve estar entre 1 e 100")

        if self.valor_por_pessoa is not None and self.valor_por_pessoa < 0:
            raise ValueError("valor_por_pessoa não pode ser negativo")

    def is_parcelada(self) -> bool:
        """Verifica se é uma transação parcelada"""
        return self.parcelas is not None and self.parcelas > 1

    def is_recorrente(self) -> bool:
        """Verifica se é uma transação recorrente (não ocasional)"""
        return (
            self.recorrencia is not None and
            self.recorrencia != Recurrence.OCASIONAL
        )

    def is_entrada(self) -> bool:
        """Verifica se é uma entrada (receita)"""
        return self.tipo == TransactionType.ENTRADA

    def is_saida(self) -> bool:
        """Verifica se é uma saída (despesa)"""
        return self.tipo == TransactionType.SAIDA

    def valor_parcela(self) -> Decimal | None:
        """Calcula o valor de cada parcela (se aplicável)"""
        if not self.is_parcelada():
            return None
        return self.valor / Decimal(self.parcelas)

    def is_gasto_compartilhado(self) -> bool:
        """Verifica se é um gasto compartilhado"""
        return self.tipo_divisao in [TipoDivisao.COMPARTILHADO_50_50, TipoDivisao.COMPARTILHADO_CUSTOM]

    def is_gasto_pessoal(self) -> bool:
        """Verifica se é um gasto pessoal"""
        return self.tipo_divisao == TipoDivisao.PESSOAL

    def __str__(self) -> str:
        divisao_str = f" ({self.tipo_divisao.value})" if self.is_gasto_compartilhado() else ""
        return f"{self.tipo.value} - {self.descricao}: R$ {self.valor:.2f}{divisao_str}"
