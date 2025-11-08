"""
Entidade de Domínio: Categoria
Representa uma categoria de transação que pode ser padrão do sistema ou customizada por usuário
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Categoria:
    """
    Entidade de domínio: Categoria

    Representa uma categoria de transação que pode ser:
    - Padrão do sistema (is_default=True, usuario_id=None)
    - Customizada por usuário (is_default=False, usuario_id=X)
    """
    id: Optional[int]
    nome: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None
    is_default: bool = False
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def __post_init__(self):
        """Valida a categoria após inicialização"""
        self._validate()

    def _validate(self):
        """Valida regras de negócio da categoria"""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome é obrigatório e não pode ser vazio")

        if len(self.nome) > 100:
            raise ValueError("Nome não pode ter mais de 100 caracteres")

        if self.descricao and len(self.descricao) > 500:
            raise ValueError("Descrição não pode ter mais de 500 caracteres")

        # Validação específica para categorias padrão
        if self.is_default and self.usuario_id is not None:
            raise ValueError("Categorias padrão não podem ter usuário associado")

        # Validação específica para categorias customizadas
        if not self.is_default and self.usuario_id is None:
            raise ValueError("Categorias customizadas devem ter usuário associado")

    def is_categoria_padrao(self) -> bool:
        """Verifica se é uma categoria padrão do sistema"""
        return self.is_default

    def is_categoria_customizada(self) -> bool:
        """Verifica se é uma categoria customizada do usuário"""
        return not self.is_default

    def pertence_ao_usuario(self, usuario_id: int) -> bool:
        """Verifica se a categoria pertence ao usuário especificado"""
        if self.is_categoria_padrao():
            return True  # Categorias padrão estão disponíveis para todos
        
        return self.usuario_id == usuario_id

    def pode_ser_editada_por(self, usuario_id: int) -> bool:
        """Verifica se a categoria pode ser editada pelo usuário especificado"""
        return self.is_categoria_customizada() and self.usuario_id == usuario_id

    def pode_ser_deletada_por(self, usuario_id: int) -> bool:
        """Verifica se a categoria pode ser deletada pelo usuário especificado"""
        return self.is_categoria_customizada() and self.usuario_id == usuario_id

    def __str__(self) -> str:
        tipo = "Padrão" if self.is_categoria_padrao() else "Customizada"
        return f"{self.nome} ({tipo})"














