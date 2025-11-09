"""
Local Repository
Implementação do repositório de locais usando SQLAlchemy
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.models import LocalModel
from src.domain.exceptions import DatabaseException, DuplicateCNPJException
from src.domain.models.local import Local
from src.ports.local_port import ILocalRepository


class LocalRepository(ILocalRepository):
    """Repositório de locais usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: LocalModel) -> Local:
        """Converte model do SQLAlchemy para entidade de domínio"""
        return Local(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            cnpj=model.cnpj,
            razao_social=model.razao_social,
            categoria=model.categoria,
            endereco=model.endereco,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, local: Local) -> LocalModel:
        """Converte entidade de domínio para model do SQLAlchemy"""
        return LocalModel(
            id=local.id,
            nome_fantasia=local.nome_fantasia,
            cnpj=local.cnpj,
            razao_social=local.razao_social,
            categoria=local.categoria,
            endereco=local.endereco
        )

    async def create(self, local: Local) -> Local:
        """Cria um novo local"""
        try:
            # Verificar se CNPJ já existe
            if local.cnpj:
                existing = await self.get_by_cnpj(local.cnpj)
                if existing:
                    raise DuplicateCNPJException(local.cnpj)

            model = self._to_model(local)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_domain(model)
        except DuplicateCNPJException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao criar local: {str(e)}", e)

    async def get_by_id(self, local_id: int) -> Local | None:
        """Busca local por ID"""
        try:
            stmt = select(LocalModel).where(LocalModel.id == local_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar local: {str(e)}", e)

    async def get_by_cnpj(self, cnpj: str) -> Local | None:
        """Busca local por CNPJ"""
        try:
            # Limpar CNPJ para busca (remover formatação)
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

            stmt = select(LocalModel).where(LocalModel.cnpj == cnpj_limpo)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar local por CNPJ: {str(e)}", e)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Local]:
        """Lista todos os locais"""
        try:
            stmt = select(LocalModel).order_by(LocalModel.nome_fantasia).limit(limit).offset(offset)
            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar locais: {str(e)}", e)

    async def update(self, local_id: int, local: Local) -> Local | None:
        """Atualiza um local"""
        try:
            stmt = select(LocalModel).where(LocalModel.id == local_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            # Verificar se está tentando atualizar CNPJ para um já existente
            if local.cnpj and local.cnpj != model.cnpj:
                existing = await self.get_by_cnpj(local.cnpj)
                if existing and existing.id != local_id:
                    raise DuplicateCNPJException(local.cnpj)

            # Atualizar campos
            model.nome_fantasia = local.nome_fantasia
            model.cnpj = local.cnpj
            model.razao_social = local.razao_social
            model.categoria = local.categoria
            model.endereco = local.endereco
            model.atualizado_em = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(model)

            return self._to_domain(model)
        except DuplicateCNPJException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao atualizar local: {str(e)}", e)

    async def delete(self, local_id: int) -> bool:
        """Remove um local"""
        try:
            stmt = select(LocalModel).where(LocalModel.id == local_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao deletar local: {str(e)}", e)

    async def count(self) -> int:
        """Conta total de locais"""
        try:
            stmt = select(func.count(LocalModel.id))
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(f"Erro ao contar locais: {str(e)}", e)
