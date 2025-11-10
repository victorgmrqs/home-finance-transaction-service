"""
Port (Interface) para Local Repository
Define o contrato que o repositório de locais deve implementar
"""

from abc import ABC, abstractmethod

from src.domain.models.local import Local


class ILocalRepository(ABC):
    """Interface para repositório de locais"""

    @abstractmethod
    async def create(self, local: Local) -> Local:
        """Cria um novo local"""
        pass

    @abstractmethod
    async def get_by_id(self, local_id: int) -> Local | None:
        """Busca local por ID"""
        pass

    @abstractmethod
    async def get_by_cnpj(self, cnpj: str) -> Local | None:
        """Busca local por CNPJ"""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Local]:
        """Lista todos os locais"""
        pass

    @abstractmethod
    async def update(self, local_id: int, local: Local) -> Local | None:
        """Atualiza um local"""
        pass

    @abstractmethod
    async def delete(self, local_id: int) -> bool:
        """Remove um local"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Conta total de locais"""
        pass
