"""
Testes de Serviço: UsuarioService
Testa a lógica de negócio da camada de aplicação para usuários
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.application.usuario_service import UsuarioService
from src.domain.models.usuario import Usuario
from src.domain.exceptions import UsuarioNotFoundException, InvalidUsuarioException, DatabaseException


class TestUsuarioService:
    """Testes para UsuarioService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório"""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        """Instância do serviço com mock do repositório"""
        return UsuarioService(mock_repository)

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

    @pytest.mark.asyncio
    async def test_create_usuario_success(self, service, mock_repository, usuario_domain):
        """Testa criação de usuário com sucesso"""
        mock_repository.create.return_value = usuario_domain

        result = await service.create_usuario(usuario_domain)

        mock_repository.create.assert_called_once_with(usuario_domain)
        assert result == usuario_domain

    @pytest.mark.asyncio
    async def test_create_usuario_database_error(self, service, mock_repository, usuario_domain):
        """Testa erro de banco de dados na criação"""
        mock_repository.create.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.create_usuario(usuario_domain)

        mock_repository.create.assert_called_once_with(usuario_domain)

    @pytest.mark.asyncio
    async def test_get_usuario_success(self, service, mock_repository, usuario_domain):
        """Testa busca de usuário por ID com sucesso"""
        usuario_id = 1
        mock_repository.get_by_id.return_value = usuario_domain

        result = await service.get_usuario(usuario_id)

        mock_repository.get_by_id.assert_called_once_with(usuario_id)
        assert result == usuario_domain

    @pytest.mark.asyncio
    async def test_get_usuario_not_found(self, service, mock_repository):
        """Testa busca de usuário por ID não encontrado"""
        usuario_id = 999
        mock_repository.get_by_id.return_value = None

        result = await service.get_usuario(usuario_id)

        mock_repository.get_by_id.assert_called_once_with(usuario_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_usuario_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na busca"""
        usuario_id = 1
        mock_repository.get_by_id.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.get_usuario(usuario_id)

        mock_repository.get_by_id.assert_called_once_with(usuario_id)

    @pytest.mark.asyncio
    async def test_get_usuario_by_email_success(self, service, mock_repository, usuario_domain):
        """Testa busca de usuário por email com sucesso"""
        email = "joao@example.com"
        mock_repository.get_by_email.return_value = usuario_domain

        result = await service.get_usuario_by_email(email)

        mock_repository.get_by_email.assert_called_once_with(email)
        assert result == usuario_domain

    @pytest.mark.asyncio
    async def test_get_usuario_by_email_not_found(self, service, mock_repository):
        """Testa busca de usuário por email não encontrado"""
        email = "naoexiste@example.com"
        mock_repository.get_by_email.return_value = None

        result = await service.get_usuario_by_email(email)

        mock_repository.get_by_email.assert_called_once_with(email)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_usuario_by_email_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na busca por email"""
        email = "joao@example.com"
        mock_repository.get_by_email.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.get_usuario_by_email(email)

        mock_repository.get_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_list_usuarios_success(self, service, mock_repository, usuario_domain):
        """Testa listagem de usuários com sucesso"""
        usuarios_list = [usuario_domain]
        total_count = 1
        mock_repository.list_all.return_value = usuarios_list
        mock_repository.count.return_value = total_count

        result = await service.list_usuarios()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, nome=None)
        mock_repository.count.assert_called_once_with(nome=None)
        assert result == (usuarios_list, total_count)

    @pytest.mark.asyncio
    async def test_list_usuarios_with_filters(self, service, mock_repository, usuario_domain):
        """Testa listagem de usuários com filtros"""
        usuarios_list = [usuario_domain]
        total_count = 1
        mock_repository.list_all.return_value = usuarios_list
        mock_repository.count.return_value = total_count

        result = await service.list_usuarios(limit=5, offset=10, nome="João")

        mock_repository.list_all.assert_called_once_with(limit=5, offset=10, nome="João")
        mock_repository.count.assert_called_once_with(nome="João")
        assert result == (usuarios_list, total_count)

    @pytest.mark.asyncio
    async def test_list_usuarios_empty(self, service, mock_repository):
        """Testa listagem de usuários vazia"""
        usuarios_list = []
        total_count = 0
        mock_repository.list_all.return_value = usuarios_list
        mock_repository.count.return_value = total_count

        result = await service.list_usuarios()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, nome=None)
        mock_repository.count.assert_called_once_with(nome=None)
        assert result == (usuarios_list, total_count)

    @pytest.mark.asyncio
    async def test_list_usuarios_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na listagem"""
        mock_repository.list_all.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.list_usuarios()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, nome=None)

    @pytest.mark.asyncio
    async def test_update_usuario_success(self, service, mock_repository, usuario_domain):
        """Testa atualização de usuário com sucesso"""
        usuario_id = 1
        usuario_atualizado = Usuario(
            id=usuario_id,
            nome="João Silva Atualizado",
            email="joao.novo@example.com",
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 2, 12, 0, 0)
        )
        mock_repository.update.return_value = usuario_atualizado

        result = await service.update_usuario(usuario_id, usuario_atualizado)

        mock_repository.update.assert_called_once_with(usuario_id, usuario_atualizado)
        assert result == usuario_atualizado

    @pytest.mark.asyncio
    async def test_update_usuario_not_found(self, service, mock_repository, usuario_domain):
        """Testa atualização de usuário não encontrado"""
        usuario_id = 999
        mock_repository.update.return_value = None

        result = await service.update_usuario(usuario_id, usuario_domain)

        mock_repository.update.assert_called_once_with(usuario_id, usuario_domain)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_usuario_database_error(self, service, mock_repository, usuario_domain):
        """Testa erro de banco de dados na atualização"""
        usuario_id = 1
        mock_repository.update.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.update_usuario(usuario_id, usuario_domain)

        mock_repository.update.assert_called_once_with(usuario_id, usuario_domain)

    @pytest.mark.asyncio
    async def test_delete_usuario_success(self, service, mock_repository):
        """Testa remoção de usuário com sucesso"""
        usuario_id = 1
        mock_repository.delete.return_value = True

        result = await service.delete_usuario(usuario_id)

        mock_repository.delete.assert_called_once_with(usuario_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_usuario_not_found(self, service, mock_repository):
        """Testa remoção de usuário não encontrado"""
        usuario_id = 999
        mock_repository.delete.return_value = False

        result = await service.delete_usuario(usuario_id)

        mock_repository.delete.assert_called_once_with(usuario_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_usuario_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na remoção"""
        usuario_id = 1
        mock_repository.delete.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.delete_usuario(usuario_id)

        mock_repository.delete.assert_called_once_with(usuario_id)

    @pytest.mark.asyncio
    async def test_create_usuario_with_invalid_data(self, service, mock_repository):
        """Testa criação de usuário com dados inválidos"""
        # Teste com nome vazio - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Usuario(
                id=None,
                nome="",  # Nome vazio
                email="test@example.com"
            )

    @pytest.mark.asyncio
    async def test_create_usuario_with_invalid_email(self, service, mock_repository):
        """Testa criação de usuário com email inválido"""
        # Teste com email inválido - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=None,
                nome="João Silva",
                email="email-invalido"  # Email sem @
            )