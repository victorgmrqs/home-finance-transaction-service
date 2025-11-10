"""
Usuario Service
Serviço de aplicação para usuários
Orquestra a lógica de negócio relacionada a usuários
"""


from src.adapters.repositories.usuario_repository import UsuarioRepository
from src.domain.models.usuario import Usuario


class UsuarioService:
    """
    Serviço de aplicação para usuários

    Coordena operações de CRUD e lógica de negócio
    """

    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    async def create_usuario(self, usuario: Usuario) -> Usuario:
        """
        Cria um novo usuário

        Args:
            usuario: Entidade de usuário a ser criada

        Returns:
            Usuario: Usuário criado com ID

        Raises:
            DatabaseException: Se erro ao salvar
        """
        # A validação já ocorre no __post_init__ da entidade
        return await self.repository.create(usuario)

    async def get_usuario(self, usuario_id: int) -> Usuario | None:
        """
        Busca usuário por ID

        Args:
            usuario_id: ID do usuário

        Returns:
            Usuario: Usuário encontrado ou None
        """
        return await self.repository.get_by_id(usuario_id)

    async def get_usuario_by_email(self, email: str) -> Usuario | None:
        """
        Busca usuário por email

        Args:
            email: Email do usuário

        Returns:
            Usuario: Usuário encontrado ou None
        """
        return await self.repository.get_by_email(email)

    async def list_usuarios(
        self,
        limit: int = 10,
        offset: int = 0,
        nome: str | None = None
    ) -> tuple[list[Usuario], int]:
        """
        Lista usuários com filtros e paginação

        Args:
            limit: Limite de resultados
            offset: Offset para paginação
            nome: Filtro por nome

        Returns:
            tuple: (lista de usuários, total de registros)
        """
        usuarios = await self.repository.list_all(
            limit=limit,
            offset=offset,
            nome=nome
        )

        total = await self.repository.count(nome=nome)

        return usuarios, total

    async def update_usuario(
        self,
        usuario_id: int,
        usuario: Usuario
    ) -> Usuario | None:
        """
        Atualiza um usuário existente

        Args:
            usuario_id: ID do usuário a atualizar
            usuario: Novos dados do usuário

        Returns:
            Usuario: Usuário atualizado ou None se não encontrado
        """
        # Atualizar (validação ocorre na entidade)
        return await self.repository.update(usuario_id, usuario)

    async def delete_usuario(self, usuario_id: int) -> bool:
        """
        Remove um usuário

        Args:
            usuario_id: ID do usuário a remover

        Returns:
            bool: True se removido, False se não encontrado
        """
        return await self.repository.delete(usuario_id)
