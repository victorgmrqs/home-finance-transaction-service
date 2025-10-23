"""
Entidade de Domínio: Painel
Representa um painel de controle financeiro vinculado a um usuário
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Painel:
    """
    Entidade de domínio: Painel

    Representa um agrupador de transações para um usuário.
    Cada painel representa um contexto financeiro específico (ex: "Casa", "Filhos", "Pessoal").

    Tipos de conta suportados:
    - CARTAO_CREDITO: Cartão de crédito
    - CONTA_BANCARIA: Conta bancária
    - DINHEIRO: Dinheiro físico
    """
    id: Optional[int]
    nome: str
    usuario_id: int
    tipo_conta: str = "CARTAO_CREDITO"
    descricao: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def __post_init__(self):
        """Valida o painel após inicialização"""
        self._validate()

    def _validate(self):
        """Valida regras de negócio do painel"""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome é obrigatório e não pode ser vazio")

        if len(self.nome) > 255:
            raise ValueError("Nome não pode ter mais de 255 caracteres")

        if self.descricao and len(self.descricao) > 1000:
            raise ValueError("Descrição não pode ter mais de 1000 caracteres")

        if self.usuario_id is None or self.usuario_id <= 0:
            raise ValueError("ID do usuário é obrigatório e deve ser maior que zero")

        # Validar tipo_conta
        tipos_validos = ['CARTAO_CREDITO', 'CONTA_BANCARIA', 'DINHEIRO']
        if self.tipo_conta not in tipos_validos:
            raise ValueError(f"tipo_conta deve ser um de: {', '.join(tipos_validos)}")

    def tem_descricao(self) -> bool:
        """Verifica se o painel possui descrição"""
        return self.descricao is not None and bool(self.descricao.strip())

    def __str__(self) -> str:
        return f"{self.nome} (Usuário: {self.usuario_id})"
