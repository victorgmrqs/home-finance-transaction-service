"""
Dashboard Service
Serviço de agregação de dados do dashboard
"""

from datetime import date

from src.adapters.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """
    Serviço de dashboard com agregações

    Consolida dados de múltiplos painéis e transações em uma única resposta
    """

    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    async def get_dashboard_summary(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        painel_ids: list[int] | None = None
    ) -> dict:
        """
        Retorna resumo completo do dashboard com todas as agregações

        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            painel_ids: Lista de IDs de painéis para filtrar (opcional)

        Returns:
            dict com resumo, por_categoria, por_painel e estatisticas
        """
        # Buscar todas as agregações em paralelo
        resumo = await self.repository.get_resumo_geral(
            usuario_id, data_inicio, data_fim, painel_ids
        )

        por_categoria = await self.repository.get_agregacao_por_categoria(
            usuario_id, data_inicio, data_fim, painel_ids
        )

        por_painel = await self.repository.get_agregacao_por_painel(
            usuario_id, data_inicio, data_fim, painel_ids
        )

        estatisticas = await self.repository.get_estatisticas(
            usuario_id, data_inicio, data_fim, painel_ids
        )

        # Determinar mês do relatório
        from datetime import datetime
        mes = data_inicio.strftime("%Y-%m") if data_inicio else datetime.now().strftime("%Y-%m")

        return {
            "mes": mes,
            "usuario_id": usuario_id,
            "resumo": resumo,
            "por_categoria": por_categoria,
            "por_painel": por_painel,
            "estatisticas": estatisticas
        }
