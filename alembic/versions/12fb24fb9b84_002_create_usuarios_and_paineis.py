"""002_create_usuarios_and_paineis

Revision ID: 12fb24fb9b84
Revises: 001_create_initial_tables
Create Date: 2025-10-04 22:59:02.777934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12fb24fb9b84'
down_revision: Union[str, Sequence[str], None] = '001_create_initial_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criação da tabela usuarios
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Criação da tabela paineis
    op.create_table(
        "paineis",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Usar batch mode para SQLite
    with op.batch_alter_table("transacoes") as batch_op:
        # Adicionar coluna painel_id
        batch_op.add_column(
            sa.Column("painel_id", sa.Integer, nullable=True)
        )

    # Criar um painel padrão para usuário padrão
    # Primeiro criar usuário padrão
    op.execute("""
        INSERT INTO usuarios (nome, email, criado_em, atualizado_em) 
        VALUES ('Usuário Padrão', 'default@example.com', datetime('now'), datetime('now'))
    """)
    
    # Criar painel padrão
    op.execute("""
        INSERT INTO paineis (nome, descricao, usuario_id, criado_em, atualizado_em) 
        VALUES ('Painel Padrão', 'Painel padrão para transações existentes', 1, datetime('now'), datetime('now'))
    """)
    
    # Atualizar todas as transações existentes para usar o painel padrão
    op.execute("UPDATE transacoes SET painel_id = 1 WHERE painel_id IS NULL")
    
    # Agora tornar a coluna NOT NULL usando batch mode
    with op.batch_alter_table("transacoes") as batch_op:
        batch_op.alter_column("painel_id", nullable=False)
        # Adicionar foreign key constraint
        batch_op.create_foreign_key(
            "fk_transacoes_painel_id",
            "paineis",
            ["painel_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # Índices
    op.create_index("idx_usuarios_nome", "usuarios", ["nome"])
    op.create_index("idx_usuarios_email", "usuarios", ["email"])
    op.create_index("idx_paineis_usuario_id", "paineis", ["usuario_id"])
    op.create_index("idx_paineis_nome_usuario", "paineis", ["nome", "usuario_id"])
    op.create_index("idx_transacoes_painel_id", "transacoes", ["painel_id"])

    # Constraint para nome único de painel por usuário
    with op.batch_alter_table("paineis") as batch_op:
        batch_op.create_unique_constraint(
            "uq_paineis_nome_usuario",
            ["nome", "usuario_id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Remover constraint e índices
    op.drop_constraint("uq_paineis_nome_usuario", "paineis", type_="unique")
    op.drop_index("idx_transacoes_painel_id", table_name="transacoes")
    op.drop_index("idx_paineis_nome_usuario", table_name="paineis")
    op.drop_index("idx_paineis_usuario_id", table_name="paineis")
    op.drop_index("idx_usuarios_email", table_name="usuarios")
    op.drop_index("idx_usuarios_nome", table_name="usuarios")

    # Remover coluna painel_id da tabela transacoes
    op.drop_column("transacoes", "painel_id")

    # Remover tabelas
    op.drop_table("paineis")
    op.drop_table("usuarios")
