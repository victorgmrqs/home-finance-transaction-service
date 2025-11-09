"""
Testes de Repositório: UsuarioRepository
Testa as operações de banco de dados para usuários
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.models import UsuarioModel
from src.adapters.repositories.usuario_repository import UsuarioRepository
from src.domain.exceptions import DatabaseException
from src.domain.models.usuario import Usuario


class TestUsuarioRepository:
    """Testes para UsuarioRepository"""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do SQLAlchemy"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Instância do repositório com mock da sessão"""
        return UsuarioRepository(mock_session)

    @pytest.fixture
    def usuario_model(self):
        """Modelo de usuário para testes"""
        return UsuarioModel(
            id=1,
            nome="João Silva",
            email="joao@example.com",
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    @pytest.fixture
    def usuario_domain(self):
        """Entidade de domínio para testes"""
        return Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com",
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    def test_to_domain(self, repository, usuario_model):
        """Testa conversão de model para domínio"""
        usuario = repository._to_domain(usuario_model)

        assert isinstance(usuario, Usuario)
        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@example.com"
        assert usuario.criado_em == usuario_model.criado_em
        assert usuario.atualizado_em == usuario_model.atualizado_em

    def test_to_model(self, repository, usuario_domain):
        """Testa conversão de domínio para model"""
        model = repository._to_model(usuario_domain)

        assert isinstance(model, UsuarioModel)
        assert model.id == 1
        assert model.nome == "João Silva"
        assert model.email == "joao@example.com"

    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, usuario_domain):
        """Testa criação de usuário com sucesso"""
        # Mock do refresh para simular o ID gerado
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda model: setattr(model, 'id', 1)

        usuario_criado = await repository.create(usuario_domain)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert usuario_criado.id == 1

    @pytest.mark.asyncio
    async def test_create_database_error(self, repository, mock_session, usuario_domain):
        """Testa erro de banco de dados na criação"""
        mock_session.commit.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao criar usuário"):
            await repository.create(usuario_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, mock_session, usuario_model):
        """Testa busca por ID com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = usuario_model
        mock_session.execute.return_value = mock_result

        usuario = await repository.get_by_id(1)

        assert usuario is not None
        assert usuario.id == 1
        assert usuario.nome == "João Silva"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Testa busca por ID quando não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        usuario = await repository.get_by_id(999)

        assert usuario is None

    @pytest.mark.asyncio
    async def test_get_by_id_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na busca por ID"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao buscar usuário"):
            await repository.get_by_id(1)

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, repository, mock_session, usuario_model):
        """Testa busca por email com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = usuario_model
        mock_session.execute.return_value = mock_result

        usuario = await repository.get_by_email("joao@example.com")

        assert usuario is not None
        assert usuario.email == "joao@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repository, mock_session):
        """Testa busca por email quando não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        usuario = await repository.get_by_email("naoexiste@example.com")

        assert usuario is None

    @pytest.mark.asyncio
    async def test_list_all_success(self, repository, mock_session, usuario_model):
        """Testa listagem de usuários com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [usuario_model]
        mock_session.execute.return_value = mock_result

        usuarios = await repository.list_all(limit=10, offset=0)

        assert len(usuarios) == 1
        assert usuarios[0].id == 1
        assert usuarios[0].nome == "João Silva"

    @pytest.mark.asyncio
    async def test_list_all_with_filters(self, repository, mock_session, usuario_model):
        """Testa listagem com filtros"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [usuario_model]
        mock_session.execute.return_value = mock_result

        usuarios = await repository.list_all(limit=10, offset=0, nome="João")

        assert len(usuarios) == 1

    @pytest.mark.asyncio
    async def test_list_all_empty(self, repository, mock_session):
        """Testa listagem quando não há usuários"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        usuarios = await repository.list_all()

        assert len(usuarios) == 0

    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, usuario_model, usuario_domain):
        """Testa atualização de usuário com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = usuario_model
        mock_session.execute.return_value = mock_result

        usuario_atualizado = await repository.update(1, usuario_domain)

        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert usuario_atualizado is not None

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session, usuario_domain):
        """Testa atualização quando usuário não encontrado"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        usuario_atualizado = await repository.update(999, usuario_domain)

        assert usuario_atualizado is None

    @pytest.mark.asyncio
    async def test_update_database_error(self, repository, mock_session, usuario_domain):
        """Testa erro de banco de dados na atualização"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao atualizar usuário"):
            await repository.update(1, usuario_domain)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_success(self, repository, mock_session, usuario_model):
        """Testa exclusão de usuário com sucesso"""
        # Mock do resultado da query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = usuario_model
        mock_session.execute.return_value = mock_result

        deleted = await repository.delete(1)

        mock_session.delete.assert_called_once_with(usuario_model)
        mock_session.commit.assert_called_once()
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Testa exclusão quando usuário não encontrado"""
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

        with pytest.raises(DatabaseException, match="Erro ao deletar usuário"):
            await repository.delete(1)

        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_success(self, repository, mock_session):
        """Testa contagem de usuários com sucesso"""
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

        count = await repository.count(nome="João")

        assert count == 2

    @pytest.mark.asyncio
    async def test_count_database_error(self, repository, mock_session):
        """Testa erro de banco de dados na contagem"""
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(DatabaseException, match="Erro ao contar usuários"):
            await repository.count()
