"""
Categoria Service
Serviço de aplicação para categorias
Orquestra a lógica de negócio relacionada a categorias
"""

from typing import Optional, List
from src.adapters.repositories.categoria_repository import CategoriaRepository
from src.domain.models.categoria import Categoria
from src.domain.exceptions import DatabaseException


class CategoriaService:
    """
    Serviço de aplicação para categorias

    Coordena operações de CRUD e lógica de negócio relacionada a categorias
    """

    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    async def create_categoria(self, categoria: Categoria) -> Categoria:
        """
        Cria uma nova categoria customizada

        Args:
            categoria: Entidade de categoria a ser criada

        Returns:
            Categoria: Categoria criada com ID

        Raises:
            DatabaseException: Se erro ao salvar ou categoria já existe
        """
        # Verificar se já existe categoria com mesmo nome para o usuário
        if categoria.usuario_id:
            existing = await self.repository.find_by_name_and_user(
                categoria.nome, categoria.usuario_id
            )
            if existing:
                raise DatabaseException(
                    f"Já existe uma categoria com o nome '{categoria.nome}' para este usuário"
                )

        return await self.repository.create(categoria)

    async def get_categoria(self, categoria_id: int) -> Optional[Categoria]:
        """
        Busca categoria por ID

        Args:
            categoria_id: ID da categoria

        Returns:
            Categoria: Categoria encontrada ou None
        """
        return await self.repository.get_by_id(categoria_id)

    async def list_categorias_for_user(self, usuario_id: int) -> List[Categoria]:
        """
        Lista todas as categorias disponíveis para um usuário:
        - Categorias padrão do sistema
        - Categorias customizadas do usuário

        Args:
            usuario_id: ID do usuário

        Returns:
            List[Categoria]: Lista de categorias disponíveis
        """
        return await self.repository.list_all_for_user(usuario_id)

    async def list_default_categories(self) -> List[Categoria]:
        """
        Lista apenas as categorias padrão do sistema

        Returns:
            List[Categoria]: Lista de categorias padrão
        """
        return await self.repository.list_default_categories()

    async def list_user_categories(self, usuario_id: int) -> List[Categoria]:
        """
        Lista apenas as categorias customizadas do usuário

        Args:
            usuario_id: ID do usuário

        Returns:
            List[Categoria]: Lista de categorias customizadas
        """
        return await self.repository.list_user_categories(usuario_id)

    async def update_categoria(
        self,
        categoria_id: int,
        categoria: Categoria,
        usuario_id: int
    ) -> Optional[Categoria]:
        """
        Atualiza uma categoria customizada

        Args:
            categoria_id: ID da categoria a atualizar
            categoria: Novos dados da categoria
            usuario_id: ID do usuário que está fazendo a atualização

        Returns:
            Categoria: Categoria atualizada ou None se não encontrada

        Raises:
            DatabaseException: Se tentar editar categoria padrão ou categoria não pertence ao usuário
        """
        # Buscar categoria existente
        existing = await self.repository.get_by_id(categoria_id)
        if not existing:
            return None

        # Verificar se é categoria padrão
        if existing.is_categoria_padrao():
            raise DatabaseException("Não é possível editar categorias padrão do sistema")

        # Verificar se pertence ao usuário
        if not existing.pode_ser_editada_por(usuario_id):
            raise DatabaseException("Você não tem permissão para editar esta categoria")

        # Verificar se novo nome já existe para o usuário
        if categoria.nome != existing.nome:
            duplicate = await self.repository.find_by_name_and_user(
                categoria.nome, usuario_id
            )
            if duplicate and duplicate.id != categoria_id:
                raise DatabaseException(
                    f"Já existe uma categoria com o nome '{categoria.nome}'"
                )

        return await self.repository.update(categoria_id, categoria)

    async def delete_categoria(self, categoria_id: int, usuario_id: int) -> bool:
        """
        Remove uma categoria customizada

        Args:
            categoria_id: ID da categoria a remover
            usuario_id: ID do usuário que está fazendo a remoção

        Returns:
            bool: True se removida, False se não encontrada

        Raises:
            DatabaseException: Se tentar deletar categoria padrão, categoria não pertence ao usuário,
                              ou categoria possui transações associadas
        """
        # Buscar categoria existente
        existing = await self.repository.get_by_id(categoria_id)
        if not existing:
            return False

        # Verificar se é categoria padrão
        if existing.is_categoria_padrao():
            raise DatabaseException("Não é possível deletar categorias padrão do sistema")

        # Verificar se pertence ao usuário
        if not existing.pode_ser_deletada_por(usuario_id):
            raise DatabaseException("Você não tem permissão para deletar esta categoria")

        # Verificar se possui transações associadas
        if await self.repository.has_transactions(categoria_id):
            raise DatabaseException(
                "Não é possível deletar categoria com transações associadas"
            )

        return await self.repository.delete(categoria_id)

    async def can_delete_categoria(self, categoria_id: int, usuario_id: int) -> bool:
        """
        Verifica se uma categoria pode ser deletada pelo usuário

        Args:
            categoria_id: ID da categoria
            usuario_id: ID do usuário

        Returns:
            bool: True se pode deletar, False caso contrário
        """
        categoria = await self.repository.get_by_id(categoria_id)
        if not categoria:
            return False

        # Não pode deletar categoria padrão
        if categoria.is_categoria_padrao():
            return False

        # Não pode deletar se não pertence ao usuário
        if not categoria.pode_ser_deletada_por(usuario_id):
            return False

        # Não pode deletar se possui transações
        if await self.repository.has_transactions(categoria_id):
            return False

        return True






