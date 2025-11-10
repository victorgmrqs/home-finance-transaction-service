"""
Port interface para Usuario Repository
Define o contrato que os repositórios de usuários devem implementar
"""

from abc import ABC, abstractmethod

from src.domain.models.usuario import Usuario


class UsuarioRepositoryPort(ABC):
    """Interface abstrata para repositório de usuários"""

    @abstractmethod
    async def create(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    async def get_by_id(self, usuario_id: int) -> Usuario | None:
        """Busca usuário por ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Usuario | None:
        """Busca usuário por email"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        nome: str | None = None
    ) -> list[Usuario]:
        """Lista usuários com filtros opcionais"""
        pass

    @abstractmethod
    async def update(self, usuario_id: int, usuario: Usuario) -> Usuario | None:
        """Atualiza um usuário"""
        pass

    @abstractmethod
    async def delete(self, usuario_id: int) -> bool:
        """Remove um usuário"""
        pass

    @abstractmethod
    async def count(self, nome: str | None = None) -> int:
        """Conta total de usuários com filtros"""
        pass
