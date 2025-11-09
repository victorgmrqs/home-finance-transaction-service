"""
Categoria Repository
Implementação do repositório de categorias usando SQLAlchemy
"""

from datetime import UTC, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.models import CategoriaModel
from src.domain.exceptions import DatabaseException
from src.domain.models.categoria import Categoria


class CategoriaRepository:
    """Repositório de categorias usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: CategoriaModel) -> Categoria:
        """Converte model do SQLAlchemy para entidade de domínio"""
        return Categoria(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            usuario_id=model.usuario_id,
            is_default=model.is_default,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, categoria: Categoria) -> CategoriaModel:
        """Converte entidade de domínio para model do SQLAlchemy"""
        return CategoriaModel(
            id=categoria.id,
            nome=categoria.nome,
            descricao=categoria.descricao,
            usuario_id=categoria.usuario_id,
            is_default=categoria.is_default
        )

    async def create(self, categoria: Categoria) -> Categoria:
        """Cria uma nova categoria"""
        try:
            model = self._to_model(categoria)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao criar categoria: {str(e)}", e)

    async def get_by_id(self, categoria_id: int) -> Categoria | None:
        """Busca categoria por ID"""
        try:
            stmt = select(CategoriaModel).where(CategoriaModel.id == categoria_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar categoria: {str(e)}", e)

    async def list_all_for_user(self, usuario_id: int) -> list[Categoria]:
        """
        Lista todas as categorias disponíveis para um usuário:
        - Categorias padrão do sistema (is_default=True)
        - Categorias customizadas do usuário (is_default=False, usuario_id=X)
        """
        try:
            stmt = select(CategoriaModel).where(
                or_(
                    CategoriaModel.is_default,  # Categorias padrão
                    and_(
                        ~CategoriaModel.is_default,
                        CategoriaModel.usuario_id == usuario_id
                    )  # Categorias customizadas do usuário
                )
            ).order_by(
                CategoriaModel.is_default.desc(),  # Padrão primeiro
                CategoriaModel.nome  # Depois por nome
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar categorias: {str(e)}", e)

    async def list_default_categories(self) -> list[Categoria]:
        """Lista apenas as categorias padrão do sistema"""
        try:
            stmt = select(CategoriaModel).where(
                CategoriaModel.is_default
            ).order_by(CategoriaModel.nome)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar categorias padrão: {str(e)}", e)

    async def list_user_categories(self, usuario_id: int) -> list[Categoria]:
        """Lista apenas as categorias customizadas do usuário"""
        try:
            stmt = select(CategoriaModel).where(
                and_(
                    ~CategoriaModel.is_default,
                    CategoriaModel.usuario_id == usuario_id
                )
            ).order_by(CategoriaModel.nome)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar categorias do usuário: {str(e)}", e)

    async def find_by_name_and_user(self, nome: str, usuario_id: int) -> Categoria | None:
        """Busca categoria por nome e usuário (para verificar duplicatas)"""
        try:
            stmt = select(CategoriaModel).where(
                and_(
                    CategoriaModel.nome == nome,
                    CategoriaModel.usuario_id == usuario_id
                )
            )
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar categoria por nome: {str(e)}", e)

    async def update(self, categoria_id: int, categoria: Categoria) -> Categoria | None:
        """Atualiza uma categoria"""
        try:
            stmt = select(CategoriaModel).where(CategoriaModel.id == categoria_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            # Atualizar campos
            model.nome = categoria.nome
            model.descricao = categoria.descricao
            model.atualizado_em = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(model)

            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao atualizar categoria: {str(e)}", e)

    async def delete(self, categoria_id: int) -> bool:
        """Remove uma categoria"""
        try:
            stmt = select(CategoriaModel).where(CategoriaModel.id == categoria_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao deletar categoria: {str(e)}", e)

    async def count_transactions_by_category(self, categoria_id: int) -> int:
        """Conta quantas transações usam esta categoria"""
        try:
            from src.adapters.repositories.models import TransactionModel

            stmt = select(func.count(TransactionModel.id)).where(
                TransactionModel.categoria == categoria_id
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(f"Erro ao contar transações da categoria: {str(e)}", e)

    async def has_transactions(self, categoria_id: int) -> bool:
        """Verifica se a categoria possui transações associadas"""
        count = await self.count_transactions_by_category(categoria_id)
        return count > 0














