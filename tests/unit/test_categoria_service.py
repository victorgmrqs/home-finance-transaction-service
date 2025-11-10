"""
Testes de Serviço: CategoriaService
Testa a lógica de negócio da camada de aplicação para categorias
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.application.categoria_service import CategoriaService
from src.domain.exceptions import DatabaseException
from src.domain.models.categoria import Categoria


class TestCategoriaService:
    """Testes para CategoriaService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repositório"""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        """Instância do serviço com mock do repositório"""
        return CategoriaService(mock_repository)

    @pytest.fixture
    def categoria_padrao(self):
        """Categoria padrão do sistema"""
        return Categoria(
            id=1,
            nome="Alimentação",
            descricao="Gastos com alimentação",
            usuario_id=None,
            is_default=True,
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    @pytest.fixture
    def categoria_customizada(self):
        """Categoria customizada do usuário"""
        return Categoria(
            id=2,
            nome="Academia",
            descricao="Gastos com academia",
            usuario_id=1,
            is_default=False,
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

    @pytest.mark.asyncio
    async def test_create_categoria_success(self, service, mock_repository, categoria_customizada):
        """Testa criação de categoria customizada com sucesso"""
        mock_repository.find_by_name_and_user.return_value = None
        mock_repository.create.return_value = categoria_customizada

        result = await service.create_categoria(categoria_customizada)

        mock_repository.find_by_name_and_user.assert_called_once_with("Academia", 1)
        mock_repository.create.assert_called_once_with(categoria_customizada)
        assert result == categoria_customizada

    @pytest.mark.asyncio
    async def test_create_categoria_duplicate_name(self, service, mock_repository, categoria_customizada):
        """Testa erro ao criar categoria com nome duplicado"""
        mock_repository.find_by_name_and_user.return_value = categoria_customizada

        with pytest.raises(DatabaseException) as exc_info:
            await service.create_categoria(categoria_customizada)

        assert "já existe uma categoria com o nome" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_categoria_success(self, service, mock_repository, categoria_padrao):
        """Testa busca de categoria por ID"""
        mock_repository.get_by_id.return_value = categoria_padrao

        result = await service.get_categoria(1)

        mock_repository.get_by_id.assert_called_once_with(1)
        assert result == categoria_padrao

    @pytest.mark.asyncio
    async def test_get_categoria_not_found(self, service, mock_repository):
        """Testa busca de categoria inexistente"""
        mock_repository.get_by_id.return_value = None

        result = await service.get_categoria(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_list_categorias_for_user(self, service, mock_repository, categoria_padrao, categoria_customizada):
        """Testa listagem de categorias para usuário"""
        categorias = [categoria_padrao, categoria_customizada]
        mock_repository.list_all_for_user.return_value = categorias

        result = await service.list_categorias_for_user(1)

        mock_repository.list_all_for_user.assert_called_once_with(1)
        assert result == categorias

    @pytest.mark.asyncio
    async def test_update_categoria_success(self, service, mock_repository, categoria_customizada):
        """Testa atualização de categoria customizada"""
        updated_categoria = Categoria(
            id=2,
            nome="Fitness",
            descricao="Academia e personal",
            usuario_id=1,
            is_default=False,
            criado_em=datetime(2025, 1, 1, 12, 0, 0),
            atualizado_em=datetime(2025, 1, 1, 12, 0, 0)
        )

        mock_repository.get_by_id.return_value = categoria_customizada
        mock_repository.find_by_name_and_user.return_value = None
        mock_repository.update.return_value = updated_categoria

        result = await service.update_categoria(2, updated_categoria, 1)

        mock_repository.get_by_id.assert_called_once_with(2)
        mock_repository.find_by_name_and_user.assert_called_once_with("Fitness", 1)
        mock_repository.update.assert_called_once_with(2, updated_categoria)
        assert result == updated_categoria

    @pytest.mark.asyncio
    async def test_update_categoria_not_found(self, service, mock_repository, categoria_customizada):
        """Testa atualização de categoria inexistente"""
        mock_repository.get_by_id.return_value = None

        result = await service.update_categoria(999, categoria_customizada, 1)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_categoria_padrao_error(self, service, mock_repository, categoria_padrao):
        """Testa erro ao tentar editar categoria padrão"""
        mock_repository.get_by_id.return_value = categoria_padrao

        with pytest.raises(DatabaseException) as exc_info:
            await service.update_categoria(1, categoria_padrao, 1)

        assert "não é possível editar categorias padrão" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_categoria_wrong_user(self, service, mock_repository, categoria_customizada):
        """Testa erro ao tentar editar categoria de outro usuário"""
        mock_repository.get_by_id.return_value = categoria_customizada

        with pytest.raises(DatabaseException) as exc_info:
            await service.update_categoria(2, categoria_customizada, 2)  # Usuário diferente

        assert "não tem permissão para editar" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_categoria_success(self, service, mock_repository, categoria_customizada):
        """Testa exclusão de categoria customizada"""
        mock_repository.get_by_id.return_value = categoria_customizada
        mock_repository.has_transactions.return_value = False
        mock_repository.delete.return_value = True

        result = await service.delete_categoria(2, 1)

        mock_repository.get_by_id.assert_called_once_with(2)
        mock_repository.has_transactions.assert_called_once_with(2)
        mock_repository.delete.assert_called_once_with(2)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_categoria_not_found(self, service, mock_repository):
        """Testa exclusão de categoria inexistente"""
        mock_repository.get_by_id.return_value = None

        result = await service.delete_categoria(999, 1)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_categoria_padrao_error(self, service, mock_repository, categoria_padrao):
        """Testa erro ao tentar deletar categoria padrão"""
        mock_repository.get_by_id.return_value = categoria_padrao

        with pytest.raises(DatabaseException) as exc_info:
            await service.delete_categoria(1, 1)

        assert "não é possível deletar categorias padrão" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_categoria_with_transactions_error(self, service, mock_repository, categoria_customizada):
        """Testa erro ao tentar deletar categoria com transações"""
        mock_repository.get_by_id.return_value = categoria_customizada
        mock_repository.has_transactions.return_value = True

        with pytest.raises(DatabaseException) as exc_info:
            await service.delete_categoria(2, 1)

        assert "transações associadas" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_can_delete_categoria_true(self, service, mock_repository, categoria_customizada):
        """Testa verificação de permissão para deletar categoria"""
        mock_repository.get_by_id.return_value = categoria_customizada
        mock_repository.has_transactions.return_value = False

        result = await service.can_delete_categoria(2, 1)

        assert result is True

    @pytest.mark.asyncio
    async def test_can_delete_categoria_false_padrao(self, service, mock_repository, categoria_padrao):
        """Testa verificação de permissão para deletar categoria padrão"""
        mock_repository.get_by_id.return_value = categoria_padrao

        result = await service.can_delete_categoria(1, 1)

        assert result is False

    @pytest.mark.asyncio
    async def test_can_delete_categoria_false_with_transactions(self, service, mock_repository, categoria_customizada):
        """Testa verificação de permissão para deletar categoria com transações"""
        mock_repository.get_by_id.return_value = categoria_customizada
        mock_repository.has_transactions.return_value = True

        result = await service.can_delete_categoria(2, 1)

        assert result is False














