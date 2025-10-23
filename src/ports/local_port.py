"""
Port (Interface) para Local Repository
Define o contrato que o repositório de locais deve implementar
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.local import Local


class ILocalRepository(ABC):
    """Interface para repositório de locais"""

    @abstractmethod
    async def create(self, local: Local) -> Local:
        """Cria um novo local"""
        pass

    @abstractmethod
    async def get_by_id(self, local_id: int) -> Optional[Local]:
        """Busca local por ID"""
        pass

    @abstractmethod
    async def get_by_cnpj(self, cnpj: str) -> Optional[Local]:
        """Busca local por CNPJ"""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Local]:
        """Lista todos os locais"""
        pass

    @abstractmethod
    async def update(self, local_id: int, local: Local) -> Optional[Local]:
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
