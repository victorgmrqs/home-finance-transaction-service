"""
Testes de Serviço: PainelService
Testa a lógica de negócio da camada de aplicação para painéis
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from src.application.painel_service import PainelService
from src.domain.models.painel import Painel
from src.domain.exceptions import PainelNotFoundException, InvalidPainelException, DatabaseException


class TestPainelService:
    """Testes para PainelService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório"""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        """Instância do serviço com mock do repositório"""
        return PainelService(mock_repository)

    @pytest.fixture
    def painel_domain(self):
        """Entidade de domínio para testes"""
        return Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="Gastos da casa",
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    @pytest.mark.asyncio
    async def test_create_painel_success(self, service, mock_repository, painel_domain):
        """Testa criação de painel com sucesso"""
        mock_repository.create.return_value = painel_domain

        result = await service.create_painel(painel_domain)

        mock_repository.create.assert_called_once_with(painel_domain)
        assert result == painel_domain

    @pytest.mark.asyncio
    async def test_create_painel_database_error(self, service, mock_repository, painel_domain):
        """Testa erro de banco de dados na criação"""
        mock_repository.create.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.create_painel(painel_domain)

        mock_repository.create.assert_called_once_with(painel_domain)

    @pytest.mark.asyncio
    async def test_get_painel_success(self, service, mock_repository, painel_domain):
        """Testa busca de painel por ID com sucesso"""
        painel_id = 1
        mock_repository.get_by_id.return_value = painel_domain

        result = await service.get_painel(painel_id)

        mock_repository.get_by_id.assert_called_once_with(painel_id)
        assert result == painel_domain

    @pytest.mark.asyncio
    async def test_get_painel_not_found(self, service, mock_repository):
        """Testa busca de painel por ID não encontrado"""
        painel_id = 999
        mock_repository.get_by_id.return_value = None

        result = await service.get_painel(painel_id)

        mock_repository.get_by_id.assert_called_once_with(painel_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_painel_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na busca"""
        painel_id = 1
        mock_repository.get_by_id.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.get_painel(painel_id)

        mock_repository.get_by_id.assert_called_once_with(painel_id)

    @pytest.mark.asyncio
    async def test_get_painel_by_usuario_and_nome_success(self, service, mock_repository, painel_domain):
        """Testa busca de painel por usuário e nome com sucesso"""
        usuario_id = 1
        nome = "Casa"
        mock_repository.get_by_usuario_and_nome.return_value = painel_domain

        result = await service.get_painel_by_usuario_and_nome(usuario_id, nome)

        mock_repository.get_by_usuario_and_nome.assert_called_once_with(usuario_id, nome)
        assert result == painel_domain

    @pytest.mark.asyncio
    async def test_get_painel_by_usuario_and_nome_not_found(self, service, mock_repository):
        """Testa busca de painel por usuário e nome não encontrado"""
        usuario_id = 1
        nome = "Não Existe"
        mock_repository.get_by_usuario_and_nome.return_value = None

        result = await service.get_painel_by_usuario_and_nome(usuario_id, nome)

        mock_repository.get_by_usuario_and_nome.assert_called_once_with(usuario_id, nome)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_painel_by_usuario_and_nome_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na busca por usuário e nome"""
        usuario_id = 1
        nome = "Casa"
        mock_repository.get_by_usuario_and_nome.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.get_painel_by_usuario_and_nome(usuario_id, nome)

        mock_repository.get_by_usuario_and_nome.assert_called_once_with(usuario_id, nome)

    @pytest.mark.asyncio
    async def test_list_paineis_by_usuario_success(self, service, mock_repository, painel_domain):
        """Testa listagem de painéis por usuário com sucesso"""
        usuario_id = 1
        paineis_list = [painel_domain]
        total_count = 1
        mock_repository.list_by_usuario.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis_by_usuario(usuario_id)

        mock_repository.list_by_usuario.assert_called_once_with(usuario_id=usuario_id, limit=10, offset=0, nome=None)
        mock_repository.count.assert_called_once_with(usuario_id=usuario_id, nome=None)
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_by_usuario_with_filters(self, service, mock_repository, painel_domain):
        """Testa listagem de painéis por usuário com filtros"""
        usuario_id = 1
        paineis_list = [painel_domain]
        total_count = 1
        mock_repository.list_by_usuario.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis_by_usuario(usuario_id, limit=5, offset=10, nome="Casa")

        mock_repository.list_by_usuario.assert_called_once_with(usuario_id=usuario_id, limit=5, offset=10, nome="Casa")
        mock_repository.count.assert_called_once_with(usuario_id=usuario_id, nome="Casa")
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_by_usuario_empty(self, service, mock_repository):
        """Testa listagem de painéis por usuário vazia"""
        usuario_id = 1
        paineis_list = []
        total_count = 0
        mock_repository.list_by_usuario.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis_by_usuario(usuario_id)

        mock_repository.list_by_usuario.assert_called_once_with(usuario_id=usuario_id, limit=10, offset=0, nome=None)
        mock_repository.count.assert_called_once_with(usuario_id=usuario_id, nome=None)
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_by_usuario_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na listagem por usuário"""
        usuario_id = 1
        mock_repository.list_by_usuario.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.list_paineis_by_usuario(usuario_id)

        mock_repository.list_by_usuario.assert_called_once_with(usuario_id=usuario_id, limit=10, offset=0, nome=None)

    @pytest.mark.asyncio
    async def test_list_paineis_success(self, service, mock_repository, painel_domain):
        """Testa listagem de painéis com sucesso"""
        paineis_list = [painel_domain]
        total_count = 1
        mock_repository.list_all.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, usuario_id=None, nome=None)
        mock_repository.count.assert_called_once_with(usuario_id=None, nome=None)
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_with_filters(self, service, mock_repository, painel_domain):
        """Testa listagem de painéis com filtros"""
        paineis_list = [painel_domain]
        total_count = 1
        mock_repository.list_all.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis(limit=5, offset=10, usuario_id=1, nome="Casa")

        mock_repository.list_all.assert_called_once_with(limit=5, offset=10, usuario_id=1, nome="Casa")
        mock_repository.count.assert_called_once_with(usuario_id=1, nome="Casa")
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_empty(self, service, mock_repository):
        """Testa listagem de painéis vazia"""
        paineis_list = []
        total_count = 0
        mock_repository.list_all.return_value = paineis_list
        mock_repository.count.return_value = total_count

        result = await service.list_paineis()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, usuario_id=None, nome=None)
        mock_repository.count.assert_called_once_with(usuario_id=None, nome=None)
        assert result == (paineis_list, total_count)

    @pytest.mark.asyncio
    async def test_list_paineis_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na listagem"""
        mock_repository.list_all.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.list_paineis()

        mock_repository.list_all.assert_called_once_with(limit=10, offset=0, usuario_id=None, nome=None)

    @pytest.mark.asyncio
    async def test_update_painel_success(self, service, mock_repository, painel_domain):
        """Testa atualização de painel com sucesso"""
        painel_id = 1
        painel_atualizado = Painel(
            id=painel_id,
            nome="Casa Atualizada",
            usuario_id=1,
            descricao="Gastos da casa atualizados",
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 2, 12, 0, 0)
        )
        mock_repository.update.return_value = painel_atualizado

        result = await service.update_painel(painel_id, painel_atualizado)

        mock_repository.update.assert_called_once_with(painel_id, painel_atualizado)
        assert result == painel_atualizado

    @pytest.mark.asyncio
    async def test_update_painel_not_found(self, service, mock_repository, painel_domain):
        """Testa atualização de painel não encontrado"""
        painel_id = 999
        mock_repository.update.return_value = None

        result = await service.update_painel(painel_id, painel_domain)

        mock_repository.update.assert_called_once_with(painel_id, painel_domain)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_painel_database_error(self, service, mock_repository, painel_domain):
        """Testa erro de banco de dados na atualização"""
        painel_id = 1
        mock_repository.update.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.update_painel(painel_id, painel_domain)

        mock_repository.update.assert_called_once_with(painel_id, painel_domain)

    @pytest.mark.asyncio
    async def test_delete_painel_success(self, service, mock_repository):
        """Testa remoção de painel com sucesso"""
        painel_id = 1
        mock_repository.delete.return_value = True

        result = await service.delete_painel(painel_id)

        mock_repository.delete.assert_called_once_with(painel_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_painel_not_found(self, service, mock_repository):
        """Testa remoção de painel não encontrado"""
        painel_id = 999
        mock_repository.delete.return_value = False

        result = await service.delete_painel(painel_id)

        mock_repository.delete.assert_called_once_with(painel_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_painel_database_error(self, service, mock_repository):
        """Testa erro de banco de dados na remoção"""
        painel_id = 1
        mock_repository.delete.side_effect = DatabaseException("Erro de conexão")

        with pytest.raises(DatabaseException, match="Erro de conexão"):
            await service.delete_painel(painel_id)

        mock_repository.delete.assert_called_once_with(painel_id)

    @pytest.mark.asyncio
    async def test_create_painel_with_invalid_data(self, service, mock_repository):
        """Testa criação de painel com dados inválidos"""
        # Teste com nome vazio - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Painel(
                id=None,
                nome="",  # Nome vazio
                usuario_id=1,
                descricao="Descrição teste"
            )

    @pytest.mark.asyncio
    async def test_create_painel_with_invalid_usuario_id(self, service, mock_repository):
        """Testa criação de painel com usuario_id inválido"""
        # Teste com usuario_id inválido - deve falhar na validação da entidade
        with pytest.raises(ValueError, match="ID do usuário é obrigatório e deve ser maior que zero"):
            Painel(
                id=None,
                nome="Painel Teste",
                usuario_id=0,  # ID inválido
                descricao="Descrição teste"
            )