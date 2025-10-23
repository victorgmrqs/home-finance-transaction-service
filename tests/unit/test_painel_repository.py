"""
Testes de Repositório: PainelRepository
Testa as operações de banco de dados para painéis
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.repositories.painel_repository import PainelRepository
from src.adapters.repositories.models import PainelModel
from src.domain.models.painel import Painel
from src.domain.exceptions import DatabaseException


class TestPainelRepository:
    """Testes para PainelRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do SQLAlchemy"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Instância do repositório com mock da sessão"""
        return PainelRepository(mock_session)

    @pytest.fixture
    def painel_model(self):
        """Modelo de painel para testes"""
        return PainelModel(
            id=1,
            nome="Casa",
            descricao="Gastos da casa",
            tipo_conta="CARTAO_CREDITO",
            usuario_id=1,
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    @pytest.fixture
    def painel_domain(self):
        """Entidade de domínio para testes"""
        return Painel(
            id=1,
            nome="Casa",
            descricao="Gastos da casa",
            tipo_conta="CARTAO_CREDITO",
            usuario_id=1,
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    def test_to_domain(self, repository, painel_model):
        """Testa conversão de model para domínio"""
        painel = repository._to_domain(painel_model)

        assert isinstance(painel, Painel)
        assert painel.id == 1
        assert painel.nome == "Casa"
        assert painel.descricao == "Gastos da casa"
        assert painel.usuario_id == 1
        assert painel.criado_em == painel_model.criado_em
        assert painel.atualizado_em == painel_model.atualizado_em

    def test_to_model(self, repository, painel_domain):
        """Testa conversão de domínio para model"""
        model = repository._to_model(painel_domain)

        assert isinstance(model, PainelModel)
        assert model.id == 1
        assert model.nome == "Casa"
        assert model.descricao == "Gastos da casa"
        assert model.usuario_id == 1

    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, painel_domain):
        """Testa criação de painel com sucesso"""
        # Mock do refresh para simular o ID gerado
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda model: setattr(model, 'id', 1)

        painel_criado = await repository.create(painel_domain)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert painel_criado.id == 1

    @pytest.mark.asyncio
    async def test_create_database_error(self, repository, mock_session, painel_domain):
        """Testa erro de banco de dados na criação"""
        mock_session.commit.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao criar painel"):
            await repository.create(painel_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, mock_session, painel_model):
        """Testa busca por ID com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = painel_model
        mock_session.execute.return_value = mock_result

        painel = await repository.get_by_id(1)

        assert painel is not None
        assert painel.id == 1
        assert painel.nome == "Casa"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Testa busca por ID quando não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        painel = await repository.get_by_id(999)

        assert painel is None

    @pytest.mark.asyncio
    async def test_get_by_usuario_and_nome_success(self, repository, mock_session, painel_model):
        """Testa busca por usuário e nome com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = painel_model
        mock_session.execute.return_value = mock_result

        painel = await repository.get_by_usuario_and_nome(1, "Casa")

        assert painel is not None
        assert painel.nome == "Casa"
        assert painel.usuario_id == 1

    @pytest.mark.asyncio
    async def test_get_by_usuario_and_nome_not_found(self, repository, mock_session):
        """Testa busca por usuário e nome quando não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        painel = await repository.get_by_usuario_and_nome(1, "Não Existe")

        assert painel is None

    @pytest.mark.asyncio
    async def test_list_by_usuario_success(self, repository, mock_session, painel_model):
        """Testa listagem de painéis por usuário com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [painel_model]
        mock_session.execute.return_value = mock_result

        paineis = await repository.list_by_usuario(usuario_id=1, limit=10, offset=0)

        assert len(paineis) == 1
        assert paineis[0].id == 1
        assert paineis[0].nome == "Casa"

    @pytest.mark.asyncio
    async def test_list_by_usuario_with_filters(self, repository, mock_session, painel_model):
        """Testa listagem por usuário com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [painel_model]
        mock_session.execute.return_value = mock_result

        paineis = await repository.list_by_usuario(
            usuario_id=1, 
            limit=10, 
            offset=0, 
            nome="Casa"
        )

        assert len(paineis) == 1

    @pytest.mark.asyncio
    async def test_list_all_success(self, repository, mock_session, painel_model):
        """Testa listagem geral de painéis com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [painel_model]
        mock_session.execute.return_value = mock_result

        paineis = await repository.list_all(limit=10, offset=0)

        assert len(paineis) == 1
        assert paineis[0].id == 1
        assert paineis[0].nome == "Casa"

    @pytest.mark.asyncio
    async def test_list_all_with_filters(self, repository, mock_session, painel_model):
        """Testa listagem geral com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [painel_model]
        mock_session.execute.return_value = mock_result

        paineis = await repository.list_all(
            limit=10, 
            offset=0, 
            usuario_id=1, 
            nome="Casa"
        )

        assert len(paineis) == 1

    @pytest.mark.asyncio
    async def test_list_all_empty(self, repository, mock_session):
        """Testa listagem quando não há painéis"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        paineis = await repository.list_all()

        assert len(paineis) == 0

    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, painel_model, painel_domain):
        """Testa atualização de painel com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = painel_model
        mock_session.execute.return_value = mock_result

        painel_atualizado = await repository.update(1, painel_domain)

        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert painel_atualizado is not None

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session, painel_domain):
        """Testa atualização quando painel não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        painel_atualizado = await repository.update(999, painel_domain)

        assert painel_atualizado is None

    @pytest.mark.asyncio
    async def test_update_database_error(self, repository, mock_session, painel_domain):
        """Testa erro de banco de dados na atualização"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao atualizar painel"):
            await repository.update(1, painel_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, repository, mock_session, painel_model):
        """Testa exclusão de painel com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = painel_model
        mock_session.execute.return_value = mock_result

        deleted = await repository.delete(1)

        mock_session.delete.assert_called_once_with(painel_model)
        mock_session.commit.assert_called_once()
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Testa exclusão quando painel não encontrado"""
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

        with pytest.raises(DatabaseException, match="Erro ao deletar painel"):
            await repository.delete(1)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_success(self, repository, mock_session):
        """Testa contagem de painéis com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        count = await repository.count()

        assert count == 3

    @pytest.mark.asyncio
    async def test_count_with_filters(self, repository, mock_session):
        """Testa contagem com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1
        mock_session.execute.return_value = mock_result

        count = await repository.count(usuario_id=1, nome="Casa")

        assert count == 1

    @pytest.mark.asyncio
    async def test_count_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na contagem"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao contar painéis"):
            await repository.count()

    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na busca por ID"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao buscar painel"):
            await repository.get_by_id(1)

    @pytest.mark.asyncio
    async def test_get_by_usuario_and_nome_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na busca por usuário e nome"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao buscar painel por usuário e nome"):
            await repository.get_by_usuario_and_nome(1, "Casa")

    @pytest.mark.asyncio
    async def test_list_by_usuario_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na listagem por usuário"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao listar painéis"):
            await repository.list_by_usuario(usuario_id=1)

    @pytest.mark.asyncio
    async def test_list_all_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na listagem geral"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao listar painéis"):
            await repository.list_all()
