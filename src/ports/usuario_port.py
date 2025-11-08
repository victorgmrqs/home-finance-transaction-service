"""
Port interface para Usuario Repository
Define o contrato que os repositórios de usuários devem implementar
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.usuario import Usuario


class UsuarioRepositoryPort(ABC):
    """Interface abstrata para repositório de usuários"""

    @abstractmethod
    async def create(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário"""
        pass

    @abstractmethod
    async def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        nome: Optional[str] = None
    ) -> List[Usuario]:
        """Lista usuários com filtros opcionais"""
        pass

    @abstractmethod
    async def update(self, usuario_id: int, usuario: Usuario) -> Optional[Usuario]:
        """Atualiza um usuário"""
        pass

    @abstractmethod
    async def delete(self, usuario_id: int) -> bool:
        """Remove um usuário"""
        pass

    @abstractmethod
    async def count(self, nome: Optional[str] = None) -> int:
        """Conta total de usuários com filtros"""
        pass
