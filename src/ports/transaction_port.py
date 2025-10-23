"""
Port (Interface) para Transaction Repository
Define o contrato que o repositório de transações deve implementar
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from src.domain.models.transaction import Transaction


class ITransactionRepository(ABC):
    """Interface para repositório de transações"""

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação"""
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Busca transação por ID"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        tipo: Optional[str] = None,
        categoria: Optional[str] = None,
        local_id: Optional[int] = None,
        painel_id: Optional[int] = None,
        descricao: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> List[Transaction]:
        """Lista transações com filtros opcionais"""
        pass

    @abstractmethod
    async def update(self, transaction_id: int, transaction: Transaction) -> Optional[Transaction]:
        """Atualiza uma transação"""
        pass

    @abstractmethod
    async def delete(self, transaction_id: int) -> bool:
        """Remove uma transação"""
        pass

    @abstractmethod
    async def count(
        self,
        tipo: Optional[str] = None,
        categoria: Optional[str] = None,
        local_id: Optional[int] = None,
        painel_id: Optional[int] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> int:
        """Conta total de transações com filtros"""
        pass
