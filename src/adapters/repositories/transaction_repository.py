"""
Transaction Repository
Implementação do repositório de transações usando SQLAlchemy
"""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.models import TransactionModel
from src.domain.exceptions import DatabaseException
from src.domain.models.transaction import Recurrence, TipoDivisao, Transaction, TransactionType
from src.ports.transaction_port import ITransactionRepository


class TransactionRepository(ITransactionRepository):
    """Repositório de transações usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TransactionModel) -> Transaction:
        """Converte model do SQLAlchemy para entidade de domínio"""
        return Transaction(
            id=model.id,
            data=model.data,
            descricao=model.descricao,
            valor=model.valor,
            tipo=TransactionType(model.tipo),
            categoria=model.categoria,
            recorrencia=Recurrence(model.recorrencia) if model.recorrencia else None,
            parcelas=model.parcelas,
            tipo_divisao=TipoDivisao(model.tipo_divisao) if model.tipo_divisao else TipoDivisao.PESSOAL,
            valor_por_pessoa=model.valor_por_pessoa,
            porcentagem_divisao=model.porcentagem_divisao,
            local_id=model.local_id,
            painel_id=model.painel_id,
            # Campos de parcelamento
            parcela_numero=model.parcela_numero,
            transacao_mae_id=model.transacao_mae_id,
            eh_parcela=model.eh_parcela,
            # Campos de recorrência
            transacao_recorrente_origem_id=model.transacao_recorrente_origem_id,
            recorrencia_ativa=model.recorrencia_ativa,
            proxima_geracao=model.proxima_geracao,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, transaction: Transaction) -> TransactionModel:
        """Converte entidade de domínio para model do SQLAlchemy"""
        return TransactionModel(
            id=transaction.id,
            data=transaction.data,
            descricao=transaction.descricao,
            valor=transaction.valor,
            tipo=transaction.tipo.value,
            categoria=transaction.categoria,
            recorrencia=transaction.recorrencia.value if transaction.recorrencia else None,
            parcelas=transaction.parcelas,
            tipo_divisao=transaction.tipo_divisao.value if transaction.tipo_divisao else "PESSOAL",
            valor_por_pessoa=transaction.valor_por_pessoa,
            porcentagem_divisao=transaction.porcentagem_divisao,
            local_id=transaction.local_id,
            painel_id=transaction.painel_id,
            # Campos de parcelamento
            parcela_numero=transaction.parcela_numero,
            transacao_mae_id=transaction.transacao_mae_id,
            eh_parcela=transaction.eh_parcela,
            # Campos de recorrência
            transacao_recorrente_origem_id=transaction.transacao_recorrente_origem_id,
            recorrencia_ativa=transaction.recorrencia_ativa,
            proxima_geracao=transaction.proxima_geracao
        )

    async def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação"""
        try:
            model = self._to_model(transaction)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao criar transação: {str(e)}", e)

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Busca transação por ID"""
        try:
            stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar transação: {str(e)}", e)

    def _build_filter_query(
        self,
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ):
        """Constrói query base com filtros (reutilizável para list e count)"""
        conditions = []

        if tipo:
            conditions.append(TransactionModel.tipo == tipo)
        if categoria:
            conditions.append(TransactionModel.categoria == categoria)
        if local_id:
            conditions.append(TransactionModel.local_id == local_id)
        if painel_id:
            conditions.append(TransactionModel.painel_id == painel_id)
        if descricao:
            conditions.append(TransactionModel.descricao.ilike(f"%{descricao}%"))
        if data_inicio:
            conditions.append(TransactionModel.data >= data_inicio)
        if data_fim:
            conditions.append(TransactionModel.data <= data_fim)

        return conditions

    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> list[Transaction]:
        """Lista transações com filtros opcionais"""
        try:
            stmt = select(TransactionModel)

            # Aplicar filtros usando helper
            conditions = self._build_filter_query(
                tipo, categoria, local_id, painel_id, descricao, data_inicio, data_fim
            )
            for condition in conditions:
                stmt = stmt.where(condition)

            # Ordenar por data decrescente
            stmt = stmt.order_by(TransactionModel.data.desc())

            # Paginação
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar transações: {str(e)}", e)

    async def update(self, transaction_id: int, transaction: Transaction) -> Transaction | None:
        """Atualiza uma transação"""
        try:
            stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            # Atualizar campos
            model.data = transaction.data
            model.descricao = transaction.descricao
            model.valor = transaction.valor
            model.tipo = transaction.tipo.value
            model.categoria = transaction.categoria
            model.recorrencia = transaction.recorrencia.value if transaction.recorrencia else None
            model.parcelas = transaction.parcelas
            model.tipo_divisao = transaction.tipo_divisao.value if transaction.tipo_divisao else "PESSOAL"
            model.valor_por_pessoa = transaction.valor_por_pessoa
            model.porcentagem_divisao = transaction.porcentagem_divisao
            model.local_id = transaction.local_id
            model.painel_id = transaction.painel_id
            # Campos de parcelamento
            model.parcela_numero = transaction.parcela_numero
            model.transacao_mae_id = transaction.transacao_mae_id
            model.eh_parcela = transaction.eh_parcela
            # Campos de recorrência
            model.transacao_recorrente_origem_id = transaction.transacao_recorrente_origem_id
            model.recorrencia_ativa = transaction.recorrencia_ativa
            model.proxima_geracao = transaction.proxima_geracao
            model.atualizado_em = datetime.now()  # Sem timezone para compatibilidade com TIMESTAMP WITHOUT TIME ZONE

            await self.session.commit()
            await self.session.refresh(model)

            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao atualizar transação: {str(e)}", e)

    async def delete(self, transaction_id: int) -> bool:
        """Remove uma transação"""
        try:
            stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao deletar transação: {str(e)}", e)

    async def count(
        self,
        tipo: str | None = None,
        categoria: str | None = None,
        local_id: int | None = None,
        painel_id: int | None = None,
        descricao: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None
    ) -> int:
        """Conta total de transações com filtros"""
        try:
            stmt = select(func.count(TransactionModel.id))

            # Aplicar filtros usando helper (DRY)
            conditions = self._build_filter_query(
                tipo, categoria, local_id, painel_id, descricao, data_inicio, data_fim
            )
            for condition in conditions:
                stmt = stmt.where(condition)

            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(f"Erro ao contar transações: {str(e)}", e)

    async def get_installments(self, transaction_mae_id: int) -> list[Transaction]:
        """Busca todas as parcelas de uma transação parcelada"""
        try:
            # Buscar a transação mãe e todas as suas filhas
            stmt = select(TransactionModel).where(
                (TransactionModel.id == transaction_mae_id) |
                (TransactionModel.transacao_mae_id == transaction_mae_id)
            ).order_by(TransactionModel.parcela_numero)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar parcelas: {str(e)}", e)
