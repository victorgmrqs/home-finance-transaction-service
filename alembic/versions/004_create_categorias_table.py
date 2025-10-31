"""create categorias table

Revision ID: 004_create_categorias_table
Revises: 003_add_fields
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa


# Revisão e dependências
revision = "004_create_categorias_table"
down_revision = "003_add_fields"
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela de categorias
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=False, default=False),
        sa.Column("criado_em", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Constraints
        sa.UniqueConstraint("nome", "usuario_id", name="unique_categoria_por_usuario"),
        sa.CheckConstraint("LENGTH(TRIM(nome)) > 0", name="check_nome_nao_vazio"),
    )

    # Índices para performance
    op.create_index("idx_categorias_usuario_id", "categorias", ["usuario_id"])
    op.create_index("idx_categorias_is_default", "categorias", ["is_default"])
    op.create_index("idx_categorias_nome", "categorias", ["nome"])

    # Inserir categorias padrão do sistema
    categorias_padrao = [
        ("Alimentação", "Gastos com alimentação, supermercado e restaurantes"),
        ("Transporte", "Gastos com transporte, combustível e estacionamento"),
        ("Moradia", "Gastos com aluguel, condomínio e manutenção da casa"),
        ("Saúde", "Gastos com médicos, farmácia e plano de saúde"),
        ("Lazer", "Gastos com entretenimento, viagens e hobbies"),
        ("Educação", "Gastos com cursos, livros e material escolar"),
        ("Salário", "Recebimento de salário e bonificações"),
        ("Trabalho", "Gastos relacionados ao trabalho"),
        ("Investimentos", "Aplicações e rendimentos financeiros"),
        ("Outros", "Outras despesas e receitas"),
    ]

    categorias_table = sa.table(
        "categorias",
        sa.column("nome", sa.String),
        sa.column("descricao", sa.Text),
        sa.column("usuario_id", sa.Integer),
        sa.column("is_default", sa.Boolean),
    )

    op.bulk_insert(
        categorias_table,
        [
            {
                "nome": nome,
                "descricao": descricao,
                "usuario_id": None,
                "is_default": True,
            }
            for nome, descricao in categorias_padrao
        ],
    )


def downgrade():
    # Reverter alterações
    op.drop_index("idx_categorias_nome", table_name="categorias")
    op.drop_index("idx_categorias_is_default", table_name="categorias")
    op.drop_index("idx_categorias_usuario_id", table_name="categorias")
    op.drop_table("categorias")

