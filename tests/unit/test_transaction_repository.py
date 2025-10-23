"""
Testes de Repositório: TransactionRepository
Testa as operações de banco de dados para transações (atualizado com painel_id)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.repositories.transaction_repository import TransactionRepository
from src.adapters.repositories.models import TransactionModel
from src.domain.models.transaction import Transaction, TransactionType, Recurrence
from src.domain.exceptions import DatabaseException


class TestTransactionRepository:
    """Testes para TransactionRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do SQLAlchemy"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Instância do repositório com mock da sessão"""
        return TransactionRepository(mock_session)

    @pytest.fixture
    def transaction_model(self):
        """Modelo de transação para testes"""
        return TransactionModel(
            id=1,
            data=date(2025, 1, 15),
            descricao="Salário",
            valor=Decimal("5000.00"),
            tipo="ENTRADA",
            categoria="salario",
            painel_id=1,
            recorrencia=None,
            parcelas=None,
            local_id=None,
            criado_em=datetime(2025, 1, 15, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 15, 12, 0, 0)
        )

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
            recorrencia=None,
            parcelas=None,
            local_id=None,
            criado_em=datetime(2025, 1, 15, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 15, 12, 0, 0)
        )

    def test_to_domain(self, repository, transaction_model):
        """Testa conversão de model para domínio"""
        transaction = repository._to_domain(transaction_model)

        assert isinstance(transaction, Transaction)
        assert transaction.id == 1
        assert transaction.descricao == "Salário"
        assert transaction.valor == Decimal("5000.00")
        assert transaction.tipo == TransactionType.ENTRADA
        assert transaction.painel_id == 1
        assert transaction.criado_em == transaction_model.criado_em
        assert transaction.atualizado_em == transaction_model.atualizado_em

    def test_to_model(self, repository, transaction_domain):
        """Testa conversão de domínio para model"""
        model = repository._to_model(transaction_domain)

        assert isinstance(model, TransactionModel)
        assert model.id == 1
        assert model.descricao == "Salário"
        assert model.valor == Decimal("5000.00")
        assert model.tipo == "ENTRADA"
        assert model.painel_id == 1

    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, transaction_domain):
        """Testa criação de transação com sucesso"""
        # Mock do refresh para simular o ID gerado
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda model: setattr(model, 'id', 1)

        transaction_criada = await repository.create(transaction_domain)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert transaction_criada.id == 1

    @pytest.mark.asyncio
    async def test_create_database_error(self, repository, mock_session, transaction_domain):
        """Testa erro de banco de dados na criação"""
        mock_session.commit.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao criar transação"):
            await repository.create(transaction_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, mock_session, transaction_model):
        """Testa busca por ID com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = transaction_model
        mock_session.execute.return_value = mock_result

        transaction = await repository.get_by_id(1)

        assert transaction is not None
        assert transaction.id == 1
        assert transaction.descricao == "Salário"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Testa busca por ID quando não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        transaction = await repository.get_by_id(999)

        assert transaction is None

    @pytest.mark.asyncio
    async def test_list_all_success(self, repository, mock_session, transaction_model):
        """Testa listagem de transações com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [transaction_model]
        mock_session.execute.return_value = mock_result

        transactions = await repository.list_all(limit=10, offset=0)

        assert len(transactions) == 1
        assert transactions[0].id == 1
        assert transactions[0].descricao == "Salário"

    @pytest.mark.asyncio
    async def test_list_all_with_filters(self, repository, mock_session, transaction_model):
        """Testa listagem com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [transaction_model]
        mock_session.execute.return_value = mock_result

        transactions = await repository.list_all(
            limit=10, 
            offset=0, 
            tipo="ENTRADA",
            categoria="salario",
            painel_id=1,
            descricao="Salário"
        )

        assert len(transactions) == 1

    @pytest.mark.asyncio
    async def test_list_all_with_painel_filter(self, repository, mock_session, transaction_model):
        """Testa listagem com filtro por painel"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [transaction_model]
        mock_session.execute.return_value = mock_result

        transactions = await repository.list_all(painel_id=1)

        assert len(transactions) == 1
        assert transactions[0].painel_id == 1

    @pytest.mark.asyncio
    async def test_list_all_empty(self, repository, mock_session):
        """Testa listagem quando não há transações"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        transactions = await repository.list_all()

        assert len(transactions) == 0

    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, transaction_model, transaction_domain):
        """Testa atualização de transação com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = transaction_model
        mock_session.execute.return_value = mock_result

        transaction_atualizada = await repository.update(1, transaction_domain)

        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert transaction_atualizada is not None

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session, transaction_domain):
        """Testa atualização quando transação não encontrada"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        transaction_atualizada = await repository.update(999, transaction_domain)

        assert transaction_atualizada is None

    @pytest.mark.asyncio
    async def test_update_database_error(self, repository, mock_session, transaction_domain):
        """Testa erro de banco de dados na atualização"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao atualizar transação"):
            await repository.update(1, transaction_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, repository, mock_session, transaction_model):
        """Testa exclusão de transação com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = transaction_model
        mock_session.execute.return_value = mock_result

        deleted = await repository.delete(1)

        mock_session.delete.assert_called_once_with(transaction_model)
        mock_session.commit.assert_called_once()
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Testa exclusão quando transação não encontrada"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        deleted = await repository.delete(999)

        assert deleted is False

    @pytest.mark.asyncio
    async def test_delete_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na exclusão"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao deletar transação"):
            await repository.delete(1)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_success(self, repository, mock_session):
        """Testa contagem de transações com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        count = await repository.count()

        assert count == 5

    @pytest.mark.asyncio
    async def test_count_with_filters(self, repository, mock_session):
        """Testa contagem com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 2
        mock_session.execute.return_value = mock_result

        count = await repository.count(tipo="ENTRADA", painel_id=1)

        assert count == 2

    @pytest.mark.asyncio
    async def test_count_with_painel_filter(self, repository, mock_session):
        """Testa contagem com filtro por painel"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        count = await repository.count(painel_id=1)

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na contagem"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao contar transações"):
            await repository.count()

    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na busca por ID"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao buscar transação"):
            await repository.get_by_id(1)

    @pytest.mark.asyncio
    async def test_list_all_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na listagem"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao listar transações"):
            await repository.list_all()

    @pytest.mark.asyncio
    async def test_transaction_with_all_fields(self, repository, mock_session):
        """Testa transação com todos os campos preenchidos"""
        transaction_completa = Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Notebook parcelado",
            valor=Decimal("3000.00"),
            tipo=TransactionType.SAIDA,
            categoria="tecnologia",
            painel_id=2,
            recorrencia=Recurrence.OCASIONAL,
            parcelas=12,
            local_id=5
        )

        # Mock do refresh para simular o ID gerado
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda model: setattr(model, 'id', 1)

        transaction_criada = await repository.create(transaction_completa)

        assert transaction_criada.id == 1
        assert transaction_criada.painel_id == 2
        assert transaction_criada.local_id == 5
        assert transaction_criada.parcelas == 12
        assert transaction_criada.recorrencia == Recurrence.OCASIONAL
