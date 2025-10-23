"""
Transaction Service
Serviço de aplicação para transações
Orquestra a lógica de negócio relacionada a transações
"""

from typing import Optional, List
from datetime import date
from src.ports.transaction_port import ITransactionRepository
from src.domain.models.transaction import Transaction
from src.domain.exceptions import TransactionNotFoundException


class TransactionService:
    """
    Serviço de aplicação para transações

    Coordena operações de CRUD e lógica de negócio
    """

    def __init__(self, repository: ITransactionRepository):
        self.repository = repository

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """
        Cria uma nova transação

        Args:
            transaction: Entidade de transação a ser criada

        Returns:
            Transaction: Transação criada com ID

        Raises:
            InvalidTransactionException: Se dados inválidos
            DatabaseException: Se erro ao salvar
        """
        # A validação já ocorre no __post_init__ da entidade
        return await self.repository.create(transaction)

    async def get_transaction(self, transaction_id: int) -> Transaction:
        """
        Busca transação por ID

        Args:
            transaction_id: ID da transação

        Returns:
            Transaction: Transação encontrada

        Raises:
            TransactionNotFoundException: Se transação não existe
        """
        transaction = await self.repository.get_by_id(transaction_id)

        if transaction is None:
            raise TransactionNotFoundException(transaction_id)

        return transaction

    async def list_transactions(
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
    ) -> tuple[List[Transaction], int]:
        """
        Lista transações com filtros e paginação

        Args:
            limit: Limite de resultados
            offset: Offset para paginação
            tipo: Filtro por tipo (ENTRADA/SAIDA)
            categoria: Filtro por categoria
            local_id: Filtro por local
            painel_id: Filtro por painel
            descricao: Busca por descrição
            data_inicio: Data inicial do filtro
            data_fim: Data final do filtro

        Returns:
            tuple: (lista de transações, total de registros)
        """
        transactions = await self.repository.list_all(
            limit=limit,
            offset=offset,
            tipo=tipo,
            categoria=categoria,
            local_id=local_id,
            painel_id=painel_id,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        total = await self.repository.count(
            tipo=tipo,
            categoria=categoria,
            local_id=local_id,
            painel_id=painel_id,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        return transactions, total

    async def update_transaction(
        self,
        transaction_id: int,
        transaction: Transaction
    ) -> Transaction:
        """
        Atualiza uma transação existente

        Args:
            transaction_id: ID da transação a atualizar
            transaction: Novos dados da transação

        Returns:
            Transaction: Transação atualizada

        Raises:
            TransactionNotFoundException: Se transação não existe
            InvalidTransactionException: Se dados inválidos
        """
        # Verificar se transação existe
        existing = await self.repository.get_by_id(transaction_id)
        if existing is None:
            raise TransactionNotFoundException(transaction_id)

        # Atualizar (validação ocorre na entidade)
        updated = await self.repository.update(transaction_id, transaction)

        if updated is None:
            raise TransactionNotFoundException(transaction_id)

        return updated

    async def delete_transaction(self, transaction_id: int) -> bool:
        """
        Remove uma transação

        Args:
            transaction_id: ID da transação a remover

        Returns:
            bool: True se removido, False se não encontrado

        Raises:
            TransactionNotFoundException: Se transação não existe
        """
        deleted = await self.repository.delete(transaction_id)

        if not deleted:
            raise TransactionNotFoundException(transaction_id)

        return True
