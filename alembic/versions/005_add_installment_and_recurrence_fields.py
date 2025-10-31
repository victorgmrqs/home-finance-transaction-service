"""add_installment_and_recurrence_fields

Revision ID: 005
Revises: 004_create_categorias_table
Create Date: 2025-10-23 17:04:13.740883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, Sequence[str], None] = '004_create_categorias_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add installment and recurrence fields to transactions."""
    from alembic import context
    import sqlite3

    # Get connection
    conn = context.get_bind()

    # Check if columns already exist (they might have been added automatically in batch migrations)
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('transacoes')]

    # Add installment fields if they don't exist
    if 'parcela_numero' not in existing_columns:
        op.add_column('transacoes', sa.Column('parcela_numero', sa.Integer(), nullable=True))
    if 'transacao_mae_id' not in existing_columns:
        op.add_column('transacoes', sa.Column('transacao_mae_id', sa.Integer(), nullable=True))
    if 'eh_parcela' not in existing_columns:
        op.add_column('transacoes', sa.Column('eh_parcela', sa.Boolean(), server_default='0', nullable=False))

    # Add recurrence fields if they don't exist
    if 'transacao_recorrente_origem_id' not in existing_columns:
        op.add_column('transacoes', sa.Column('transacao_recorrente_origem_id', sa.Integer(), nullable=True))
    if 'recorrencia_ativa' not in existing_columns:
        op.add_column('transacoes', sa.Column('recorrencia_ativa', sa.Boolean(), server_default='1', nullable=False))
    if 'proxima_geracao' not in existing_columns:
        op.add_column('transacoes', sa.Column('proxima_geracao', sa.Date(), nullable=True))

    # Check existing indexes
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('transacoes')]

    # Create indexes for new fields if they don't exist
    if 'idx_transacoes_transacao_mae' not in existing_indexes:
        op.create_index('idx_transacoes_transacao_mae', 'transacoes', ['transacao_mae_id'], unique=False)
    if 'idx_transacoes_recorrente_origem' not in existing_indexes:
        op.create_index('idx_transacoes_recorrente_origem', 'transacoes', ['transacao_recorrente_origem_id'], unique=False)
    if 'idx_transacoes_proxima_geracao' not in existing_indexes:
        op.create_index('idx_transacoes_proxima_geracao', 'transacoes', ['proxima_geracao'], unique=False)
    if 'idx_transacoes_eh_parcela' not in existing_indexes:
        op.create_index('idx_transacoes_eh_parcela', 'transacoes', ['eh_parcela'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove installment and recurrence fields."""
    # Drop indexes
    op.drop_index('idx_transacoes_eh_parcela', table_name='transacoes')
    op.drop_index('idx_transacoes_proxima_geracao', table_name='transacoes')
    op.drop_index('idx_transacoes_recorrente_origem', table_name='transacoes')
    op.drop_index('idx_transacoes_transacao_mae', table_name='transacoes')

    # Drop columns
    op.drop_column('transacoes', 'proxima_geracao')
    op.drop_column('transacoes', 'recorrencia_ativa')
    op.drop_column('transacoes', 'transacao_recorrente_origem_id')
    op.drop_column('transacoes', 'eh_parcela')
    op.drop_column('transacoes', 'transacao_mae_id')
    op.drop_column('transacoes', 'parcela_numero')
