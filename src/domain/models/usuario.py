"""
Entidade de Domínio: Usuario
Representa um usuário do sistema que pode possuir múltiplos painéis de controle financeiro
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Usuario:
    """
    Entidade de domínio: Usuário

    Representa uma pessoa que utiliza o sistema, podendo possuir múltiplos painéis
    de controle financeiro para organizar suas transações por contexto.
    """
    id: int | None
    nome: str
    email: str | None = None
    password_hash: str | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    def __post_init__(self):
        """Valida o usuário após inicialização"""
        self._validate()

    def _validate(self):
        """Valida regras de negócio do usuário"""
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome é obrigatório e não pode ser vazio")

        if len(self.nome) > 255:
            raise ValueError("Nome não pode ter mais de 255 caracteres")

        if self.email and len(self.email) > 255:
            raise ValueError("Email não pode ter mais de 255 caracteres")

        if self.email is not None and not self._validar_email(self.email):
            raise ValueError("Email inválido")

    def _validar_email(self, email: str) -> bool:
        """
        Valida formato básico do email

        Verifica se o email tem formato válido básico (contém @ e domínio).
        Validação completa pode ser implementada futuramente.
        """
        if not email or '@' not in email:
            return False

        partes = email.split('@')
        if len(partes) != 2:
            return False

        local, dominio = partes
        if not local or not dominio or '.' not in dominio:
            return False

        return True

    def tem_email(self) -> bool:
        """Verifica se o usuário possui email cadastrado"""
        return self.email is not None and bool(self.email.strip())

    def __str__(self) -> str:
        return f"{self.nome} ({self.email or 'sem email'})"
