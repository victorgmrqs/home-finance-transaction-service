"""003_add_tipo_conta_and_divisao_fields

Revision ID: 003_add_tipo_conta_and_divisao_fields
Revises: 12fb24fb9b84
Create Date: 2025-10-13

Adiciona:
- tipo_conta na tabela paineis (CARTAO_CREDITO, CONTA_BANCARIA, DINHEIRO)
- tipo_divisao, valor_por_pessoa, porcentagem_divisao na tabela transacoes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import CheckConstraint


# revision identifiers, used by Alembic.
revision: str = '003_add_tipo_conta_and_divisao_fields'
down_revision: Union[str, Sequence[str], None] = '12fb24fb9b84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Adiciona novos campos para v2.0."""

    # ============================================
    # MIGRATION 1: Adicionar tipo_conta em paineis
    # ============================================

    # Usar batch mode para compatibilidade com SQLite
    with op.batch_alter_table("paineis") as batch_op:
        # 1. Adicionar coluna com valor padrão para compatibilidade
        batch_op.add_column(
            sa.Column("tipo_conta", sa.String(20), nullable=False, server_default="CARTAO_CREDITO")
        )

        # 2. Adicionar constraint para validar valores
        batch_op.create_check_constraint(
            "check_tipo_conta",
            "tipo_conta IN ('CARTAO_CREDITO', 'CONTA_BANCARIA', 'DINHEIRO')"
        )

    # 3. Criar índice para melhorar performance
    op.create_index("idx_paineis_tipo_conta", "paineis", ["tipo_conta"])

    # ============================================
    # MIGRATION 2: Adicionar campos de divisão em transacoes
    # ============================================

    # Usar batch mode para compatibilidade com SQLite
    with op.batch_alter_table("transacoes") as batch_op:
        # 1. Adicionar coluna tipo_divisao com valor padrão
        batch_op.add_column(
            sa.Column("tipo_divisao", sa.String(30), nullable=False, server_default="PESSOAL")
        )

        # 2. Adicionar coluna valor_por_pessoa (calculado no frontend)
        batch_op.add_column(
            sa.Column("valor_por_pessoa", sa.Numeric(12, 2), nullable=True)
        )

        # 3. Adicionar coluna porcentagem_divisao (para divisão customizada)
        batch_op.add_column(
            sa.Column("porcentagem_divisao", sa.Integer, nullable=True)
        )

        # 4. Adicionar constraints para validação
        batch_op.create_check_constraint(
            "check_tipo_divisao",
            "tipo_divisao IN ('PESSOAL', 'COMPARTILHADO_50_50', 'COMPARTILHADO_CUSTOM')"
        )

        batch_op.create_check_constraint(
            "check_porcentagem_divisao",
            "porcentagem_divisao IS NULL OR (porcentagem_divisao > 0 AND porcentagem_divisao <= 100)"
        )

        batch_op.create_check_constraint(
            "check_valor_por_pessoa",
            "valor_por_pessoa IS NULL OR valor_por_pessoa >= 0"
        )

    # 5. Criar índice para melhorar queries de gastos compartilhados
    op.create_index("idx_transacoes_tipo_divisao", "transacoes", ["tipo_divisao"])

    # Comentários para PostgreSQL (ignorados em SQLite)
    try:
        op.execute("COMMENT ON COLUMN paineis.tipo_conta IS 'Tipo de conta: CARTAO_CREDITO, CONTA_BANCARIA ou DINHEIRO'")
        op.execute("COMMENT ON COLUMN transacoes.tipo_divisao IS 'Tipo de divisão: PESSOAL, COMPARTILHADO_50_50 ou COMPARTILHADO_CUSTOM'")
        op.execute("COMMENT ON COLUMN transacoes.valor_por_pessoa IS 'Valor que cada pessoa paga (calculado no frontend)'")
        op.execute("COMMENT ON COLUMN transacoes.porcentagem_divisao IS 'Porcentagem customizada para divisão (1-100)'")
    except Exception:
        # SQLite não suporta COMMENT, ignorar
        pass


def downgrade() -> None:
    """Downgrade schema - Remove campos adicionados."""

    # Remover índice e colunas da tabela transacoes
    op.drop_index("idx_transacoes_tipo_divisao", table_name="transacoes")

    with op.batch_alter_table("transacoes") as batch_op:
        batch_op.drop_constraint("check_valor_por_pessoa", type_="check")
        batch_op.drop_constraint("check_porcentagem_divisao", type_="check")
        batch_op.drop_constraint("check_tipo_divisao", type_="check")
        batch_op.drop_column("porcentagem_divisao")
        batch_op.drop_column("valor_por_pessoa")
        batch_op.drop_column("tipo_divisao")

    # Remover índice e coluna da tabela paineis
    op.drop_index("idx_paineis_tipo_conta", table_name="paineis")

    with op.batch_alter_table("paineis") as batch_op:
        batch_op.drop_constraint("check_tipo_conta", type_="check")
        batch_op.drop_column("tipo_conta")
