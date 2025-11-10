"""
SQLAlchemy ORM Models
Define os modelos de banco de dados usando SQLAlchemy
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()  # type: ignore[assignment, misc, valid-type, name-defined]


class UsuarioModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela usuarios"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    paineis = relationship("PainelModel", back_populates="usuario", cascade="all, delete-orphan")
    categorias = relationship("CategoriaModel", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"


class PainelModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela paineis"""
    __tablename__ = "paineis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo_conta = Column(String(20), nullable=False, server_default="CARTAO_CREDITO", index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    usuario = relationship("UsuarioModel", back_populates="paineis")
    transacoes = relationship("TransactionModel", back_populates="painel")
    compartilhamentos = relationship("PainelUsuarioModel", back_populates="painel", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("nome", "usuario_id", name="uq_paineis_nome_usuario"),
        CheckConstraint(
            "tipo_conta IN ('CARTAO_CREDITO', 'CONTA_BANCARIA', 'DINHEIRO')",
            name="check_tipo_conta"
        ),
        Index("idx_paineis_nome_usuario", "nome", "usuario_id"),
        Index("idx_paineis_tipo_conta", "tipo_conta"),
    )

    def __repr__(self):
        return f"<Painel(id={self.id}, nome='{self.nome}', usuario_id={self.usuario_id})>"


class PainelUsuarioModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela painel_usuarios (compartilhamento)"""
    __tablename__ = "painel_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    painel_id = Column(
        Integer,
        ForeignKey("paineis.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tipo_permissao = Column(String(20), nullable=False, server_default="VIEWER", index=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    painel = relationship("PainelModel", back_populates="compartilhamentos")
    usuario = relationship("UsuarioModel")

    # Constraints
    __table_args__ = (
        UniqueConstraint("painel_id", "usuario_id", name="uk_painel_usuario"),
        CheckConstraint(
            "tipo_permissao IN ('OWNER', 'EDITOR', 'VIEWER')",
            name="chk_tipo_permissao"
        ),
    )

    def __repr__(self):
        return f"<PainelUsuario(id={self.id}, painel_id={self.painel_id}, usuario_id={self.usuario_id}, permissao='{self.tipo_permissao}')>"


class LocalModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela locais"""
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String(255), nullable=True)
    cnpj = Column(String(18), unique=True, nullable=True, index=True)
    razao_social = Column(String(255), nullable=True)
    categoria = Column(String(100), nullable=True)
    endereco = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    transacoes = relationship("TransactionModel", back_populates="local")

    def __repr__(self):
        return f"<Local(id={self.id}, nome_fantasia='{self.nome_fantasia}', cnpj='{self.cnpj}')>"


class TransactionModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela transacoes"""
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, index=True)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    tipo = Column(String(10), nullable=False, index=True)
    categoria = Column(String(100), nullable=False, index=True)
    recorrencia = Column(String(20), nullable=True)
    parcelas = Column(Integer, nullable=True)
    tipo_divisao = Column(String(30), nullable=False, server_default="PESSOAL", index=True)
    valor_por_pessoa = Column(Numeric(12, 2), nullable=True)
    porcentagem_divisao = Column(Integer, nullable=True)
    local_id = Column(
        Integer,
        ForeignKey("locais.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    painel_id = Column(
        Integer,
        ForeignKey("paineis.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Campos de parcelamento
    parcela_numero = Column(Integer, nullable=True, comment="Número desta parcela (1, 2, 3...) se for parcelada")
    transacao_mae_id = Column(
        Integer,
        ForeignKey("transacoes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID da primeira parcela (null se for a parcela 1)"
    )
    eh_parcela = Column(Boolean, nullable=False, server_default="false", comment="True se faz parte de um parcelamento")

    # Campos de recorrência
    transacao_recorrente_origem_id = Column(
        Integer,
        ForeignKey("transacoes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID da transação recorrente original que gerou esta"
    )
    recorrencia_ativa = Column(Boolean, nullable=False, server_default="true", comment="Se False, para de gerar novas recorrências")
    proxima_geracao = Column(Date, nullable=True, comment="Próxima data em que deve gerar recorrência")

    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    local = relationship("LocalModel", back_populates="transacoes")
    painel = relationship("PainelModel", back_populates="transacoes")

    # Relacionamentos auto-referenciais (parcelamento e recorrência)
    parcelas_filhas = relationship(
        "TransactionModel",
        foreign_keys=[transacao_mae_id],
        remote_side=[id],
        backref="transacao_mae",
        cascade="all, delete-orphan",
        single_parent=True
    )
    transacoes_geradas = relationship(
        "TransactionModel",
        foreign_keys=[transacao_recorrente_origem_id],
        remote_side=[id],
        backref="transacao_recorrente_origem"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ENTRADA', 'SAIDA')",
            name="chk_tipo"
        ),
        CheckConstraint(
            "recorrencia IN ('DIARIO', 'SEMANAL', 'MENSAL', 'OCASIONAL')",
            name="chk_recorrencia"
        ),
        CheckConstraint(
            "parcelas IS NULL OR parcelas > 0",
            name="chk_parcelas_positivo"
        ),
        CheckConstraint(
            "tipo_divisao IN ('PESSOAL', 'COMPARTILHADO_50_50', 'COMPARTILHADO_CUSTOM')",
            name="check_tipo_divisao"
        ),
        CheckConstraint(
            "porcentagem_divisao IS NULL OR (porcentagem_divisao > 0 AND porcentagem_divisao <= 100)",
            name="check_porcentagem_divisao"
        ),
        CheckConstraint(
            "valor_por_pessoa IS NULL OR valor_por_pessoa >= 0",
            name="check_valor_por_pessoa"
        ),
        Index("idx_transacoes_data_tipo", "data", "tipo"),
        Index("idx_transacoes_categoria_tipo", "categoria", "tipo"),
        Index("idx_transacoes_painel_data", "painel_id", "data"),
        Index("idx_transacoes_tipo_divisao", "tipo_divisao"),
        Index("idx_transacoes_transacao_mae", "transacao_mae_id"),
        Index("idx_transacoes_recorrente_origem", "transacao_recorrente_origem_id"),
        Index("idx_transacoes_proxima_geracao", "proxima_geracao"),
        Index("idx_transacoes_eh_parcela", "eh_parcela"),
    )

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, data='{self.data}', "
            f"descricao='{self.descricao}', valor={self.valor}, tipo='{self.tipo}')>"
        )


class CategoriaModel(Base):  # type: ignore[misc, valid-type]
    """Modelo ORM para a tabela categorias"""
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    is_default = Column(Boolean, nullable=False, default=False, index=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relacionamento
    usuario = relationship("UsuarioModel")

    # Constraints
    __table_args__ = (
        UniqueConstraint("nome", "usuario_id", name="unique_categoria_por_usuario"),
        CheckConstraint("LENGTH(TRIM(nome)) > 0", name="check_nome_nao_vazio"),
        Index("idx_categorias_nome_usuario", "nome", "usuario_id"),
    )

    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}', is_default={self.is_default}, usuario_id={self.usuario_id})>"
