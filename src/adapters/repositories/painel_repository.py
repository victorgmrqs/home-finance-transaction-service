"""
Painel Repository
Implementação do repositório de painéis usando SQLAlchemy
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.domain.models.painel import Painel
from src.adapters.repositories.models import PainelModel
from src.domain.exceptions import DatabaseException, DuplicatePainelException


class PainelRepository:
    """Repositório de painéis usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: PainelModel) -> Painel:
        """Converte model do SQLAlchemy para entidade de domínio"""
        return Painel(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            tipo_conta=model.tipo_conta,
            usuario_id=model.usuario_id,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, painel: Painel) -> PainelModel:
        """Converte entidade de domínio para model do SQLAlchemy"""
        return PainelModel(
            id=painel.id,
            nome=painel.nome,
            descricao=painel.descricao,
            tipo_conta=painel.tipo_conta,
            usuario_id=painel.usuario_id
        )

    async def create(self, painel: Painel) -> Painel:
        """Cria um novo painel"""
        try:
            model = self._to_model(painel)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            # Verificar se é erro de constraint única
            if "uq_paineis_nome_usuario" in str(e) or "UNIQUE constraint failed" in str(e):
                raise DuplicatePainelException(painel.nome, painel.usuario_id)
            raise DatabaseException(f"Erro ao criar painel: {str(e)}", e)

    async def get_by_id(self, painel_id: int) -> Optional[Painel]:
        """Busca painel por ID"""
        try:
            stmt = select(PainelModel).where(PainelModel.id == painel_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar painel: {str(e)}", e)

    async def get_by_usuario_and_nome(self, usuario_id: int, nome: str) -> Optional[Painel]:
        """Busca painel por usuário e nome"""
        try:
            stmt = select(PainelModel).where(
                PainelModel.usuario_id == usuario_id,
                PainelModel.nome == nome
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar painel por usuário e nome: {str(e)}", e)

    async def list_by_usuario(
        self,
        usuario_id: int,
        limit: int = 10,
        offset: int = 0,
        nome: Optional[str] = None
    ) -> List[Painel]:
        """Lista painéis de um usuário com filtros opcionais"""
        try:
            stmt = select(PainelModel).where(PainelModel.usuario_id == usuario_id)

            # Aplicar filtros
            if nome:
                stmt = stmt.where(PainelModel.nome.ilike(f"%{nome}%"))

            # Ordenar por nome
            stmt = stmt.order_by(PainelModel.nome)

            # Paginação
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar painéis: {str(e)}", e)

    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        usuario_id: Optional[int] = None,
        nome: Optional[str] = None
    ) -> List[Painel]:
        """Lista painéis com filtros opcionais"""
        try:
            stmt = select(PainelModel)

            # Aplicar filtros
            if usuario_id:
                stmt = stmt.where(PainelModel.usuario_id == usuario_id)
            if nome:
                stmt = stmt.where(PainelModel.nome.ilike(f"%{nome}%"))

            # Ordenar por nome
            stmt = stmt.order_by(PainelModel.nome)

            # Paginação
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar painéis: {str(e)}", e)

    async def update(self, painel_id: int, painel: Painel) -> Optional[Painel]:
        """Atualiza um painel"""
        try:
            stmt = select(PainelModel).where(PainelModel.id == painel_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            # Atualizar campos
            model.nome = painel.nome
            model.descricao = painel.descricao
            model.tipo_conta = painel.tipo_conta
            model.atualizado_em = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(model)

            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao atualizar painel: {str(e)}", e)

    async def delete(self, painel_id: int) -> bool:
        """Remove um painel"""
        try:
            stmt = select(PainelModel).where(PainelModel.id == painel_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao deletar painel: {str(e)}", e)

    async def count(
        self,
        usuario_id: Optional[int] = None,
        nome: Optional[str] = None
    ) -> int:
        """Conta total de painéis com filtros"""
        try:
            stmt = select(func.count(PainelModel.id))

            if usuario_id:
                stmt = stmt.where(PainelModel.usuario_id == usuario_id)
            if nome:
                stmt = stmt.where(PainelModel.nome.ilike(f"%{nome}%"))

            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(f"Erro ao contar painéis: {str(e)}", e)
