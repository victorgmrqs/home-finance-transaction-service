"""
Testes de Serviço: TransactionService
Testa a lógica de negócio da camada de aplicação para transações
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from decimal import Decimal
from src.application.transaction_service import TransactionService
from src.domain.models.transaction import Transaction, TransactionType, Recurrence
from src.domain.exceptions import TransactionNotFoundException, InvalidTransactionException, DatabaseException
from src.ports.transaction_port import ITransactionRepository
from src.ports.local_port import ILocalRepository


class TestTransactionService:
    """Testes para TransactionService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório de transações"""
        return AsyncMock(spec=ITransactionRepository)

    @pytest.fixture
    def mock_local_repository(self):
        """Mock do repositório de locais"""
        return AsyncMock(spec=ILocalRepository)

    @pytest.fixture
    def service(self, mock_repository, mock_local_repository):
        """Instância do serviço com mocks dos repositórios"""
        return TransactionService(mock_repository)

    @pytest.fixture
    def transaction_domain(self):
        """Entidade de domínio para testes"""
        return Transaction(
            id=1,
            data=date(2025, 1, 15),
            descricao="Salário",
            valor=Decimal("5000.00"),
            tipo=TransactionType.ENTRADA,
            categoria="salario",
            painel_id=1,
            criado_em=datetime(2025, 1, 15, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 15, 12, 0, 0)
        )

    @pytest.mark.asyncio
    async def test_create_transaction_success(self, service, mock_repository, transaction_domain):
        """Testa criação de transação com sucesso"""
        mock_repository.create.return_value = transaction_domain

        result = await service.create_transaction(transaction_domain)

        mock_repository.create.assert_called_once_with(transaction_domain)
        assert result == transaction_domain

    @pytest.mark.asyncio
    async def test_create_transaction_database_error(self, service, mock_repository, transaction_domain):
        """Testa erro de banco de dados na criação"""
        mock_repository.create.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.create_transaction(transaction_domain)

        mock_repository.create.assert_called_once_with(transaction_domain)

    @pytest.mark.asyncio
    async def test_get_transaction_success(self, service, mock_repository, transaction_domain):
        """Testa busca de transação por ID com sucesso"""
        transaction_id = 1
        mock_repository.get_by_id.return_value = transaction_domain

        result = await service.get_transaction(transaction_id)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)
        assert result == transaction_domain

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, service, mock_repository):
        """Testa busca de transação por ID não encontrado"""
        transaction_id = 999
        mock_repository.get_by_id.return_value = None

        with pytest.raises(TransactionNotFoundException, match="Transação com ID 999 não encontrada"):
            await service.get_transaction(transaction_id)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)

    @pytest.mark.asyncio
    async def test_get_transaction_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na busca"""
        transaction_id = 1
        mock_repository.get_by_id.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.get_transaction(transaction_id)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)

    @pytest.mark.asyncio
    async def test_list_transactions_success(self, service, mock_repository, transaction_domain):
        """Testa listagem de transações com sucesso"""
        transactions_list = [transaction_domain]
        total_count = 1
        mock_repository.list_all.return_value = transactions_list
        mock_repository.count.return_value = total_count

        result = await service.list_transactions()

        mock_repository.list_all.assert_called_once_with(
            limit=10, offset=0, tipo=None, categoria=None, local_id=None, painel_id=None, descricao=None, data_inicio=None, data_fim=None
        )
        mock_repository.count.assert_called_once_with(
            tipo=None, categoria=None, local_id=None, painel_id=None, descricao=None, data_inicio=None, data_fim=None
        )
        assert result == (transactions_list, total_count)

    @pytest.mark.asyncio
    async def test_list_transactions_with_filters(self, service, mock_repository, transaction_domain):
        """Testa listagem de transações com filtros"""
        transactions_list = [transaction_domain]
        total_count = 1
        mock_repository.list_all.return_value = transactions_list
        mock_repository.count.return_value = total_count

        result = await service.list_transactions(
            limit=5, offset=10, tipo="ENTRADA", categoria="salario", painel_id=1, descricao="Salário"
        )

        mock_repository.list_all.assert_called_once_with(
            limit=5, offset=10, tipo="ENTRADA", categoria="salario", local_id=None, painel_id=1, descricao="Salário", data_inicio=None, data_fim=None
        )
        mock_repository.count.assert_called_once_with(
            tipo="ENTRADA", categoria="salario", local_id=None, painel_id=1, descricao="Salário", data_inicio=None, data_fim=None
        )
        assert result == (transactions_list, total_count)

    @pytest.mark.asyncio
    async def test_list_transactions_with_painel_filter(self, service, mock_repository, transaction_domain):
        """Testa listagem de transações com filtro por painel"""
        painel_id_filter = 1
        transactions_list = [transaction_domain]
        total_count = 1
        mock_repository.list_all.return_value = transactions_list
        mock_repository.count.return_value = total_count

        result = await service.list_transactions(painel_id=painel_id_filter)

        mock_repository.list_all.assert_called_once_with(
            limit=10, offset=0, tipo=None, categoria=None, local_id=None, painel_id=painel_id_filter, descricao=None, data_inicio=None, data_fim=None
        )
        mock_repository.count.assert_called_once_with(
            tipo=None, categoria=None, local_id=None, painel_id=painel_id_filter, descricao=None, data_inicio=None, data_fim=None
        )
        assert result == (transactions_list, total_count)

    @pytest.mark.asyncio
    async def test_list_transactions_empty(self, service, mock_repository):
        """Testa listagem de transações vazia"""
        transactions_list = []
        total_count = 0
        mock_repository.list_all.return_value = transactions_list
        mock_repository.count.return_value = total_count

        result = await service.list_transactions()

        mock_repository.list_all.assert_called_once_with(
            limit=10, offset=0, tipo=None, categoria=None, local_id=None, painel_id=None, descricao=None, data_inicio=None, data_fim=None
        )
        mock_repository.count.assert_called_once_with(
            tipo=None, categoria=None, local_id=None, painel_id=None, descricao=None, data_inicio=None, data_fim=None
        )
        assert result == (transactions_list, total_count)

    @pytest.mark.asyncio
    async def test_list_transactions_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na listagem"""
        mock_repository.list_all.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.list_transactions()

        mock_repository.list_all.assert_called_once_with(
            limit=10, offset=0, tipo=None, categoria=None, local_id=None, painel_id=None, descricao=None, data_inicio=None, data_fim=None
        )

    @pytest.mark.asyncio
    async def test_update_transaction_success(self, service, mock_repository, transaction_domain):
        """Testa atualização de transação com sucesso"""
        transaction_id = 1
        transaction_atualizada = Transaction(
            id=transaction_id,
            data=date(2025, 1, 15),
            descricao="Salário Atualizado",
            valor=Decimal("5500.00"),
            tipo=TransactionType.ENTRADA,
            categoria="salario",
            painel_id=1,
            criado_em=datetime(2025, 1, 15, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 16, 12, 0, 0)
        )
        mock_repository.get_by_id.return_value = transaction_domain
        mock_repository.update.return_value = transaction_atualizada

        result = await service.update_transaction(transaction_id, transaction_atualizada)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)
        mock_repository.update.assert_called_once_with(transaction_id, transaction_atualizada)
        assert result == transaction_atualizada

    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, service, mock_repository, transaction_domain):
        """Testa atualização de transação não encontrada"""
        transaction_id = 999
        mock_repository.get_by_id.return_value = None

        with pytest.raises(TransactionNotFoundException, match="Transação com ID 999 não encontrada"):
            await service.update_transaction(transaction_id, transaction_domain)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)
        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_transaction_update_fails(self, service, mock_repository, transaction_domain):
        """Testa falha na atualização após encontrar a transação"""
        transaction_id = 1
        mock_repository.get_by_id.return_value = transaction_domain
        mock_repository.update.return_value = None

        with pytest.raises(TransactionNotFoundException, match="Transação com ID 1 não encontrada"):
            await service.update_transaction(transaction_id, transaction_domain)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)
        mock_repository.update.assert_called_once_with(transaction_id, transaction_domain)

    @pytest.mark.asyncio
    async def test_update_transaction_database_error(self, service, mock_repository, transaction_domain):
        """Testa erro de banco de dados na atualização"""
        transaction_id = 1
        mock_repository.get_by_id.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.update_transaction(transaction_id, transaction_domain)

        mock_repository.get_by_id.assert_called_once_with(transaction_id)
        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_transaction_success(self, service, mock_repository):
        """Testa remoção de transação com sucesso"""
        transaction_id = 1
        mock_repository.delete.return_value = True

        result = await service.delete_transaction(transaction_id)

        mock_repository.delete.assert_called_once_with(transaction_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, service, mock_repository):
        """Testa remoção de transação não encontrada"""
        transaction_id = 999
        mock_repository.delete.return_value = False

        with pytest.raises(TransactionNotFoundException, match="Transação com ID 999 não encontrada"):
            await service.delete_transaction(transaction_id)

        mock_repository.delete.assert_called_once_with(transaction_id)

    @pytest.mark.asyncio
    async def test_delete_transaction_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na remoção"""
        transaction_id = 1
        mock_repository.delete.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.delete_transaction(transaction_id)

        mock_repository.delete.assert_called_once_with(transaction_id)

    @pytest.mark.asyncio
    async def test_create_transaction_with_invalid_data(self, service, mock_repository):
        """Testa criação de transação com dados inválidos"""
        # Teste com descrição vazia - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="Descrição é obrigatória e não pode ser vazia"):
            Transaction(
                id=None,
                data=date(2025, 1, 15),
                descricao="",  # Descrição vazia
                valor=Decimal("100.00"),
                tipo=TransactionType.SAIDA,
                categoria="compras",
                painel_id=1
            )

    @pytest.mark.asyncio
    async def test_create_transaction_with_invalid_valor(self, service, mock_repository):
        """Testa criação de transação com valor inválido"""
        # Teste com valor zero - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="Valor deve ser maior que zero"):
            Transaction(
                id=None,
                data=date(2025, 1, 15),
                descricao="Compra",
                valor=Decimal("0.00"),  # Valor zero
                tipo=TransactionType.SAIDA,
                categoria="compras",
                painel_id=1
            )

    @pytest.mark.asyncio
    async def test_create_transaction_with_invalid_painel_id(self, service, mock_repository):
        """Testa criação de transação com painel_id inválido"""
        # Teste com painel_id inválido - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="ID do painel é obrigatório e deve ser maior que zero"):
            Transaction(
                id=None,
                data=date(2025, 1, 15),
                descricao="Compra",
                valor=Decimal("100.00"),
                tipo=TransactionType.SAIDA,
                categoria="compras",
                painel_id=0  # ID inválido
            )