"""
Dashboard Repository
Implementação do repositório de dashboard com queries de agregação
"""

from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.models import PainelModel, TransactionModel
from src.domain.exceptions import DatabaseException


class DashboardRepository:
    """Repositório de dashboard com agregações SQL"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_resumo_geral(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        painel_ids: list[int] | None = None
    ) -> dict:
        """
        Retorna resumo geral de receitas, despesas e saldo

        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            painel_ids: Lista de IDs de painéis para filtrar (opcional)

        Returns:
            dict com total_receitas, total_despesas, saldo, total_transacoes
        """
        try:
            # Query para receitas
            stmt_receitas = select(
                func.coalesce(func.sum(TransactionModel.valor), 0).label("total"),
                func.count(TransactionModel.id).label("quantidade")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                and_(
                    PainelModel.usuario_id == usuario_id,
                    TransactionModel.tipo == "ENTRADA"
                )
            )

            # Query para despesas
            stmt_despesas = select(
                func.coalesce(func.sum(TransactionModel.valor), 0).label("total"),
                func.count(TransactionModel.id).label("quantidade")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                and_(
                    PainelModel.usuario_id == usuario_id,
                    TransactionModel.tipo == "SAIDA"
                )
            )

            # Aplicar filtros de data
            if data_inicio:
                stmt_receitas = stmt_receitas.where(TransactionModel.data >= data_inicio)
                stmt_despesas = stmt_despesas.where(TransactionModel.data >= data_inicio)
            if data_fim:
                stmt_receitas = stmt_receitas.where(TransactionModel.data <= data_fim)
                stmt_despesas = stmt_despesas.where(TransactionModel.data <= data_fim)

            # Aplicar filtro de painéis
            if painel_ids:
                stmt_receitas = stmt_receitas.where(TransactionModel.painel_id.in_(painel_ids))
                stmt_despesas = stmt_despesas.where(TransactionModel.painel_id.in_(painel_ids))

            # Executar queries
            result_receitas = await self.session.execute(stmt_receitas)
            receitas = result_receitas.one()

            result_despesas = await self.session.execute(stmt_despesas)
            despesas = result_despesas.one()

            total_receitas = float(receitas.total)
            total_despesas = float(despesas.total)

            return {
                "total_receitas": total_receitas,
                "total_despesas": total_despesas,
                "saldo": total_receitas - total_despesas,
                "total_transacoes": receitas.quantidade + despesas.quantidade
            }

        except Exception as e:
            raise DatabaseException(f"Erro ao buscar resumo geral: {str(e)}", e)

    async def get_agregacao_por_categoria(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        painel_ids: list[int] | None = None
    ) -> list[dict]:
        """
        Retorna agregação por categoria com totais e percentuais

        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            painel_ids: Lista de IDs de painéis para filtrar (opcional)

        Returns:
            Lista de dicts com categoria, total, quantidade, percentual
        """
        try:
            # Query com JOIN para obter nome da categoria
            stmt = select(
                TransactionModel.categoria.label("categoria_nome"),
                func.sum(TransactionModel.valor).label("total"),
                func.count(TransactionModel.id).label("quantidade")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                and_(
                    PainelModel.usuario_id == usuario_id,
                    TransactionModel.tipo == "SAIDA"  # Apenas despesas
                )
            )

            # Aplicar filtros de data
            if data_inicio:
                stmt = stmt.where(TransactionModel.data >= data_inicio)
            if data_fim:
                stmt = stmt.where(TransactionModel.data <= data_fim)

            # Aplicar filtro de painéis
            if painel_ids:
                stmt = stmt.where(TransactionModel.painel_id.in_(painel_ids))

            # Group by e order by
            stmt = stmt.group_by(TransactionModel.categoria).order_by(func.sum(TransactionModel.valor).desc())

            result = await self.session.execute(stmt)
            rows = result.all()

            # Calcular total geral para percentuais
            total_geral = sum(float(row.total) for row in rows)

            # Formatar resposta com percentuais
            categorias = []
            for row in rows:
                total = float(row.total)
                percentual = (total / total_geral * 100) if total_geral > 0 else 0.0

                categorias.append({
                    "categoria": row.categoria_nome,
                    "total": total,
                    "quantidade": row.quantidade,
                    "percentual": round(percentual, 2)
                })

            return categorias

        except Exception as e:
            raise DatabaseException(f"Erro ao buscar agregação por categoria: {str(e)}", e)

    async def get_agregacao_por_painel(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        painel_ids: list[int] | None = None
    ) -> list[dict]:
        """
        Retorna agregação por painel com receitas, despesas e saldo

        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            painel_ids: Lista de IDs de painéis para filtrar (opcional)

        Returns:
            Lista de dicts com painel_id, nome, receitas, despesas, saldo
        """
        try:
            # Query com agregação por painel e tipo
            stmt = select(
                PainelModel.id.label("painel_id"),
                PainelModel.nome.label("painel_nome"),
                TransactionModel.tipo,
                func.sum(TransactionModel.valor).label("total")
            ).select_from(PainelModel).outerjoin(
                TransactionModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                PainelModel.usuario_id == usuario_id
            )

            # Aplicar filtros de data
            if data_inicio:
                stmt = stmt.where(
                    (TransactionModel.data >= data_inicio) | (TransactionModel.data.is_(None))
                )
            if data_fim:
                stmt = stmt.where(
                    (TransactionModel.data <= data_fim) | (TransactionModel.data.is_(None))
                )

            # Aplicar filtro de painéis
            if painel_ids:
                stmt = stmt.where(PainelModel.id.in_(painel_ids))

            # Group by e order by
            stmt = stmt.group_by(
                PainelModel.id,
                PainelModel.nome,
                TransactionModel.tipo
            ).order_by(PainelModel.nome)

            result = await self.session.execute(stmt)
            rows = result.all()

            # Agrupar por painel
            paineis_dict: dict[int, dict] = {}
            for row in rows:
                painel_id = row.painel_id

                if painel_id not in paineis_dict:
                    paineis_dict[painel_id] = {
                        "painel_id": painel_id,
                        "painel_nome": row.painel_nome,
                        "tipo_conta": None,  # Será preenchido na query abaixo
                        "total_receitas": 0.0,
                        "total_despesas": 0.0,
                        "saldo": 0.0,
                        "quantidade_transacoes": 0
                    }

                if row.tipo == "ENTRADA":
                    paineis_dict[painel_id]["total_receitas"] = float(row.total or 0)
                elif row.tipo == "SAIDA":
                    paineis_dict[painel_id]["total_despesas"] = float(row.total or 0)

            # Buscar tipo_conta e quantidade de transações para cada painel
            if paineis_dict:
                painel_ids_list = list(paineis_dict.keys())
                stmt_paineis = select(
                    PainelModel.id,
                    PainelModel.tipo_conta,
                    func.count(TransactionModel.id).label("quantidade")
                ).select_from(PainelModel).outerjoin(
                    TransactionModel, TransactionModel.painel_id == PainelModel.id
                ).where(
                    PainelModel.id.in_(painel_ids_list)
                )

                # Aplicar filtros de data se existirem
                if data_inicio:
                    stmt_paineis = stmt_paineis.where(
                        (TransactionModel.data >= data_inicio) | (TransactionModel.data.is_(None))
                    )
                if data_fim:
                    stmt_paineis = stmt_paineis.where(
                        (TransactionModel.data <= data_fim) | (TransactionModel.data.is_(None))
                    )

                stmt_paineis = stmt_paineis.group_by(PainelModel.id, PainelModel.tipo_conta)

                result_paineis = await self.session.execute(stmt_paineis)
                paineis_info = result_paineis.all()

                for painel_info in paineis_info:
                    painel_id = painel_info.id
                    if painel_id in paineis_dict:
                        paineis_dict[painel_id]["tipo_conta"] = painel_info.tipo_conta
                        paineis_dict[painel_id]["quantidade_transacoes"] = painel_info.quantidade or 0

            # Calcular saldo
            paineis_list = []
            for painel_data in paineis_dict.values():
                painel_data["saldo"] = painel_data["total_receitas"] - painel_data["total_despesas"]
                paineis_list.append(painel_data)

            return paineis_list

        except Exception as e:
            raise DatabaseException(f"Erro ao buscar agregação por painel: {str(e)}", e)

    async def get_estatisticas(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        painel_ids: list[int] | None = None
    ) -> dict:
        """
        Retorna estatísticas gerais (min, max, média) separadas por tipo

        Args:
            usuario_id: ID do usuário
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            painel_ids: Lista de IDs de painéis para filtrar (opcional)

        Returns:
            dict com media_diaria, maior_despesa, menor_despesa, maior_receita, menor_receita
        """
        try:
            # Query para min/max de despesas
            stmt_despesas = select(
                func.min(TransactionModel.valor).label("min_valor"),
                func.max(TransactionModel.valor).label("max_valor"),
                func.sum(TransactionModel.valor).label("total"),
                func.count(func.distinct(TransactionModel.data)).label("dias_unicos")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                and_(
                    PainelModel.usuario_id == usuario_id,
                    TransactionModel.tipo == "SAIDA"
                )
            )

            # Aplicar filtros
            if data_inicio:
                stmt_despesas = stmt_despesas.where(TransactionModel.data >= data_inicio)
            if data_fim:
                stmt_despesas = stmt_despesas.where(TransactionModel.data <= data_fim)
            if painel_ids:
                stmt_despesas = stmt_despesas.where(TransactionModel.painel_id.in_(painel_ids))

            result_despesas = await self.session.execute(stmt_despesas)
            despesas = result_despesas.one()

            # Query para min/max de receitas
            stmt_receitas = select(
                func.min(TransactionModel.valor).label("min_valor"),
                func.max(TransactionModel.valor).label("max_valor")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                and_(
                    PainelModel.usuario_id == usuario_id,
                    TransactionModel.tipo == "ENTRADA"
                )
            )

            # Aplicar filtros
            if data_inicio:
                stmt_receitas = stmt_receitas.where(TransactionModel.data >= data_inicio)
            if data_fim:
                stmt_receitas = stmt_receitas.where(TransactionModel.data <= data_fim)
            if painel_ids:
                stmt_receitas = stmt_receitas.where(TransactionModel.painel_id.in_(painel_ids))

            result_receitas = await self.session.execute(stmt_receitas)
            receitas = result_receitas.one()

            # Calcular média diária de despesas
            media_diaria = 0.0
            if despesas.dias_unicos and despesas.dias_unicos > 0:
                media_diaria = float(despesas.total or 0) / despesas.dias_unicos

            # Query para min/max de todas as transações (receitas + despesas)
            stmt_all = select(
                func.min(TransactionModel.valor).label("min_valor"),
                func.max(TransactionModel.valor).label("max_valor")
            ).select_from(TransactionModel).join(
                PainelModel, TransactionModel.painel_id == PainelModel.id
            ).where(
                PainelModel.usuario_id == usuario_id
            )

            # Aplicar filtros
            if data_inicio:
                stmt_all = stmt_all.where(TransactionModel.data >= data_inicio)
            if data_fim:
                stmt_all = stmt_all.where(TransactionModel.data <= data_fim)
            if painel_ids:
                stmt_all = stmt_all.where(TransactionModel.painel_id.in_(painel_ids))

            result_all = await self.session.execute(stmt_all)
            all_transactions = result_all.one()

            return {
                "media_diaria": round(media_diaria, 2),
                "transacao_min": float(all_transactions.min_valor or 0),
                "transacao_max": float(all_transactions.max_valor or 0),
                "maior_despesa": float(despesas.max_valor or 0),
                "menor_despesa": float(despesas.min_valor or 0),
                "maior_receita": float(receitas.max_valor or 0),
                "menor_receita": float(receitas.min_valor or 0)
            }

        except Exception as e:
            raise DatabaseException(f"Erro ao buscar estatísticas: {str(e)}", e)
