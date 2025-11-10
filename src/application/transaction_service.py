"""
Transaction Service
Serviço de aplicação para transações
Orquestra a lógica de negócio relacionada a transações
"""

from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta  # type: ignore[import-untyped]

from src.domain.exceptions import TransactionNotFoundException
from src.domain.models.transaction import Transaction
from src.ports.transaction_port import ITransactionRepository


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

        Se a transação tiver parcelas > 1, cria automaticamente todas as parcelas.

        Args:
            transaction: Entidade de transação a ser criada

        Returns:
            Transaction: Transação criada com ID (primeira parcela se parcelado)

        Raises:
            InvalidTransactionException: Se dados inválidos
            DatabaseException: Se erro ao salvar
        """
        # A validação já ocorre no __post_init__ da entidade

        # Se não for parcelada, criar transação simples
        if not transaction.parcelas or transaction.parcelas <= 1:
            return await self.repository.create(transaction)

        # Criar transação parcelada
        return await self._create_installment_transactions(transaction)

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
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> tuple[list[Transaction], int]:
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

    async def _create_installment_transactions(self, transaction: Transaction) -> Transaction:
        """
        Cria múltiplas transações para parcelamento

        Args:
            transaction: Transação base com informações de parcelamento

        Returns:
            Transaction: Primeira parcela criada (transação "mãe")
        """
        parcelas = transaction.parcelas
        if parcelas is None:
            raise ValueError("Transação deve ter número de parcelas definido")
        valor_total = transaction.valor
        data_base = transaction.data

        # Calcular valor de cada parcela
        valor_parcela = Decimal(str(valor_total / parcelas)).quantize(Decimal('0.01'))

        # Ajustar primeira parcela para compensar arredondamento
        valor_primeira_parcela = valor_total - (valor_parcela * (parcelas - 1))

        transacoes_criadas: list[Transaction] = []

        # Criar todas as parcelas
        for i in range(1, parcelas + 1):
            # Calcular data da parcela (adicionar meses)
            data_parcela = data_base + relativedelta(months=i-1)

            # Valor da parcela (primeira parcela pode ser diferente devido ao arredondamento)
            valor = valor_primeira_parcela if i == 1 else valor_parcela

            # Descrição com número da parcela
            descricao_parcela = f"{transaction.descricao} - Parcela {i}/{parcelas}"

            # Criar transação parcela
            parcela = Transaction(
                id=None,
                data=data_parcela,
                descricao=descricao_parcela,
                valor=valor,
                tipo=transaction.tipo,
                categoria=transaction.categoria,
                painel_id=transaction.painel_id,
                recorrencia=transaction.recorrencia,
                parcelas=parcelas,
                tipo_divisao=transaction.tipo_divisao,
                valor_por_pessoa=transaction.valor_por_pessoa,
                porcentagem_divisao=transaction.porcentagem_divisao,
                local_id=transaction.local_id,
                # Campos de parcelamento
                parcela_numero=i,
                transacao_mae_id=transacoes_criadas[0].id if i > 1 else None,
                eh_parcela=True,
                # Campos de recorrência (transações parceladas não são recorrentes automaticamente)
                transacao_recorrente_origem_id=None,
                recorrencia_ativa=False,
                proxima_geracao=None
            )

            # Salvar parcela no banco
            parcela_criada = await self.repository.create(parcela)
            transacoes_criadas.append(parcela_criada)

            # Atualizar transacao_mae_id das parcelas subsequentes
            if i == 1:
                # Primeira parcela criada, atualizar as próximas para referenciá-la
                pass  # As próximas já terão o ID correto no loop

        # Retornar primeira parcela (transação "mãe")
        return transacoes_criadas[0]

    async def list_installments(self, transaction_id: int) -> list[Transaction]:
        """
        Lista todas as parcelas de uma transação parcelada

        Args:
            transaction_id: ID de qualquer parcela da transação parcelada

        Returns:
            List[Transaction]: Lista de todas as parcelas ordenadas por número

        Raises:
            TransactionNotFoundException: Se transação não existe
        """
        # Buscar a transação
        transaction = await self.get_transaction(transaction_id)

        # Se não for uma parcela, retornar apenas ela mesma
        if not transaction.eh_parcela:
            return [transaction]

        # Encontrar a transação mãe
        if transaction.id is None:
            raise ValueError("Transação deve ter ID para buscar parcelas")
        mae_id = transaction.transacao_mae_id if transaction.transacao_mae_id else transaction.id

        # Buscar todas as parcelas (incluindo a mãe)
        return await self.repository.get_installments(mae_id)
