"""
Painel Service
Serviço de aplicação para painéis
Orquestra a lógica de negócio relacionada a painéis
"""

from datetime import date
from decimal import Decimal

from src.adapters.repositories.painel_repository import PainelRepository
from src.adapters.repositories.transaction_repository import TransactionRepository
from src.domain.exceptions import DatabaseException
from src.domain.models.painel import Painel


class PainelService:
    """
    Serviço de aplicação para painéis

    Coordena operações de CRUD e lógica de negócio
    """

    def __init__(self, repository: PainelRepository, transaction_repository: TransactionRepository | None = None):
        self.repository = repository
        self.transaction_repository = transaction_repository

    async def create_painel(self, painel: Painel) -> Painel:
        """
        Cria um novo painel

        Args:
            painel: Entidade de painel a ser criada

        Returns:
            Painel: Painel criado com ID

        Raises:
            DatabaseException: Se erro ao salvar
        """
        # A validação já ocorre no __post_init__ da entidade
        return await self.repository.create(painel)

    async def get_painel(self, painel_id: int) -> Painel | None:
        """
        Busca painel por ID

        Args:
            painel_id: ID do painel

        Returns:
            Painel: Painel encontrado ou None
        """
        return await self.repository.get_by_id(painel_id)

    async def get_painel_by_usuario_and_nome(self, usuario_id: int, nome: str) -> Painel | None:
        """
        Busca painel por usuário e nome

        Args:
            usuario_id: ID do usuário
            nome: Nome do painel

        Returns:
            Painel: Painel encontrado ou None
        """
        return await self.repository.get_by_usuario_and_nome(usuario_id, nome)

    async def list_paineis_by_usuario(
        self,
        usuario_id: int,
        limit: int = 10,
        offset: int = 0,
        nome: str | None = None
    ) -> tuple[list[Painel], int]:
        """
        Lista painéis de um usuário com filtros e paginação

        Args:
            usuario_id: ID do usuário
            limit: Limite de resultados
            offset: Offset para paginação
            nome: Filtro por nome

        Returns:
            tuple: (lista de painéis, total de registros)
        """
        paineis = await self.repository.list_by_usuario(
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
            nome=nome
        )

        total = await self.repository.count(usuario_id=usuario_id, nome=nome)

        return paineis, total

    async def list_paineis(
        self,
        limit: int = 10,
        offset: int = 0,
        usuario_id: int | None = None,
        nome: str | None = None
    ) -> tuple[list[Painel], int]:
        """
        Lista painéis com filtros e paginação

        Args:
            limit: Limite de resultados
            offset: Offset para paginação
            usuario_id: Filtro por usuário
            nome: Filtro por nome

        Returns:
            tuple: (lista de painéis, total de registros)
        """
        paineis = await self.repository.list_all(
            limit=limit,
            offset=offset,
            usuario_id=usuario_id,
            nome=nome
        )

        total = await self.repository.count(usuario_id=usuario_id, nome=nome)

        return paineis, total

    async def update_painel(
        self,
        painel_id: int,
        painel: Painel
    ) -> Painel | None:
        """
        Atualiza um painel existente

        Args:
            painel_id: ID do painel a atualizar
            painel: Novos dados do painel

        Returns:
            Painel: Painel atualizado ou None se não encontrado
        """
        # Atualizar (validação ocorre na entidade)
        return await self.repository.update(painel_id, painel)

    async def delete_painel(self, painel_id: int) -> bool:
        """
        Remove um painel

        Args:
            painel_id: ID do painel a remover

        Returns:
            bool: True se removido, False se não encontrado
        """
        return await self.repository.delete(painel_id)

    async def calcular_balanco(
        self,
        painel_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> dict:
        """
        Calcula o balanço de um painel

        Args:
            painel_id: ID do painel
            data_inicio: Data inicial do período (opcional)
            data_fim: Data final do período (opcional)

        Returns:
            dict: Balanço com total_entradas, total_saidas, saldo, quantidade_transacoes
        """
        if not self.transaction_repository:
            raise DatabaseException("TransactionRepository não foi fornecido ao PainelService")

        # Buscar painel
        painel = await self.repository.get_by_id(painel_id)
        if not painel:
            raise DatabaseException(f"Painel {painel_id} não encontrado")

        # Buscar transações do painel
        transacoes_entradas = await self.transaction_repository.list_all(
            painel_id=painel_id,
            tipo="ENTRADA",
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=999999,
            offset=0
        )

        transacoes_saidas = await self.transaction_repository.list_all(
            painel_id=painel_id,
            tipo="SAIDA",
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=999999,
            offset=0
        )

        # Calcular totais
        total_entradas = sum(t.valor for t in transacoes_entradas)
        total_saidas = sum(t.valor for t in transacoes_saidas)
        saldo = total_entradas - total_saidas
        quantidade_transacoes = len(transacoes_entradas) + len(transacoes_saidas)

        return {
            "painel_id": painel_id,
            "nome_painel": painel.nome,
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim,
            "total_entradas": Decimal(str(total_entradas)),
            "total_saidas": Decimal(str(total_saidas)),
            "saldo": Decimal(str(saldo)),
            "quantidade_transacoes": quantidade_transacoes
        }
