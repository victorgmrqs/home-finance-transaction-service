"""
Port (Interface) para Transaction Repository
Define o contrato que o repositório de transações deve implementar
"""

from abc import ABC, abstractmethod
from datetime import date

from src.domain.models.transaction import Transaction


class ITransactionRepository(ABC):
    """Interface para repositório de transações"""

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação"""
        pass

    @abstractmethod
    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Busca transação por ID"""
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> list[Transaction]:
        """Lista transações com filtros opcionais"""
        pass

    @abstractmethod
    async def update(self, transaction_id: int, transaction: Transaction) -> Transaction | None:
        """Atualiza uma transação"""
        pass

    @abstractmethod
    async def delete(self, transaction_id: int) -> bool:
        """Remove uma transação"""
        pass

    @abstractmethod
    async def count(
        self,
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> int:
        """Conta total de transações com filtros"""
        pass

    @abstractmethod
    async def get_installments(self, transaction_mae_id: int) -> list[Transaction]:
        """Busca todas as parcelas de uma transação parcelada"""
        pass
