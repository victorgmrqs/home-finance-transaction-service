"""
Local Service
Serviço de aplicação para locais
Orquestra a lógica de negócio relacionada a locais
"""

from typing import Optional, List
from src.ports.local_port import ILocalRepository
from src.domain.models.local import Local
from src.domain.exceptions import LocalNotFoundException


class LocalService:
    """
    Serviço de aplicação para locais

    Coordena operações de CRUD e lógica de negócio
    Implementa regras conforme ADR-002
    """

    def __init__(self, repository: ILocalRepository):
        self.repository = repository

    async def create_local(self, local: Local) -> Local:
        """
        Cria um novo local

        Args:
            local: Entidade de local a ser criada

        Returns:
            Local: Local criado com ID

        Raises:
            InvalidLocalException: Se dados inválidos
            DuplicateCNPJException: Se CNPJ já existe
            DatabaseException: Se erro ao salvar
        """
        # A validação já ocorre no __post_init__ da entidade
        # Repository verifica CNPJ duplicado
        return await self.repository.create(local)

    async def get_local(self, local_id: int) -> Local:
        """
        Busca local por ID

        Args:
            local_id: ID do local

        Returns:
            Local: Local encontrado

        Raises:
            LocalNotFoundException: Se local não existe
        """
        local = await self.repository.get_by_id(local_id)

        if local is None:
            raise LocalNotFoundException(local_id)

        return local

    async def get_local_by_cnpj(self, cnpj: str) -> Optional[Local]:
        """
        Busca local por CNPJ

        Args:
            cnpj: CNPJ do local (com ou sem formatação)

        Returns:
            Optional[Local]: Local encontrado ou None
        """
        return await self.repository.get_by_cnpj(cnpj)

    async def list_locais(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Local], int]:
        """
        Lista locais com paginação

        Args:
            limit: Limite de resultados
            offset: Offset para paginação

        Returns:
            tuple: (lista de locais, total de registros)
        """
        locais = await self.repository.list_all(limit=limit, offset=offset)
        total = await self.repository.count()

        return locais, total

    async def update_local(self, local_id: int, local: Local) -> Local:
        """
        Atualiza um local existente

        Args:
            local_id: ID do local a atualizar
            local: Novos dados do local

        Returns:
            Local: Local atualizado

        Raises:
            LocalNotFoundException: Se local não existe
            DuplicateCNPJException: Se novo CNPJ já existe
            InvalidLocalException: Se dados inválidos
        """
        # Verificar se local existe
        existing = await self.repository.get_by_id(local_id)
        if existing is None:
            raise LocalNotFoundException(local_id)

        # Atualizar (validação e verificação de CNPJ duplicado no repository)
        updated = await self.repository.update(local_id, local)

        if updated is None:
            raise LocalNotFoundException(local_id)

        return updated

    async def delete_local(self, local_id: int) -> bool:
        """
        Remove um local

        Nota: Se houver transações vinculadas, o local_id será setado para NULL
        conforme configuração de CASCADE no banco (ondelete='SET NULL')

        Args:
            local_id: ID do local a remover

        Returns:
            bool: True se removido

        Raises:
            LocalNotFoundException: Se local não existe
        """
        deleted = await self.repository.delete(local_id)

        if not deleted:
            raise LocalNotFoundException(local_id)

        return True
