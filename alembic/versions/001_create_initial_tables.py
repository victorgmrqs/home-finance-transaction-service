"""create initial tables

Revision ID: 001_create_initial_tables
Revises: 
Create Date: 2025-09-28

"""
from alembic import op
import sqlalchemy as sa


# Revisão e dependências
revision = "001_create_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Criação da tabela locais
    op.create_table(
        "locais",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("nome_fantasia", sa.String(255), nullable=True),
        sa.Column("cnpj", sa.String(18), unique=True, nullable=True),
        sa.Column("razao_social", sa.String(255), nullable=True),
        sa.Column("categoria", sa.String(100), nullable=True),
        sa.Column("endereco", sa.Text, nullable=True),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Criação da tabela transacoes
    op.create_table(
        "transacoes",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("data", sa.Date, nullable=False),
        sa.Column("descricao", sa.String(255), nullable=False),
        sa.Column("valor", sa.Numeric(12, 2), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.CheckConstraint("tipo IN ('ENTRADA', 'SAIDA')", name="chk_tipo"),
        sa.Column("categoria", sa.String(100), nullable=False),
        sa.Column("recorrencia", sa.String(20), nullable=True),
        sa.CheckConstraint(
            "recorrencia IN ('DIARIO', 'SEMANAL', 'MENSAL', 'OCASIONAL')",
            name="chk_recorrencia"
        ),
        sa.Column("parcelas", sa.Integer, nullable=True),
        sa.Column("local_id", sa.Integer, sa.ForeignKey("locais.id", ondelete="SET NULL")),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices
    op.create_index("idx_transacoes_data", "transacoes", ["data"])
    op.create_index("idx_transacoes_tipo", "transacoes", ["tipo"])
    op.create_index("idx_transacoes_categoria", "transacoes", ["categoria"])
    op.create_index("idx_transacoes_local_id", "transacoes", ["local_id"])


def downgrade():
    # Reverter alterações
    op.drop_index("idx_transacoes_local_id", table_name="transacoes")
    op.drop_index("idx_transacoes_categoria", table_name="transacoes")
    op.drop_index("idx_transacoes_tipo", table_name="transacoes")
    op.drop_index("idx_transacoes_data", table_name="transacoes")
    op.drop_table("transacoes")
    op.drop_table("locais")
