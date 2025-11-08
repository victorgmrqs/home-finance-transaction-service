"""
Usuario Repository
Implementação do repositório de usuários usando SQLAlchemy
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.domain.models.usuario import Usuario
from src.adapters.repositories.models import UsuarioModel
from src.domain.exceptions import DatabaseException


class UsuarioRepository:
    """Repositório de usuários usando SQLAlchemy"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UsuarioModel) -> Usuario:
        """Converte model do SQLAlchemy para entidade de domínio"""
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            password_hash=model.password_hash,
            criado_em=model.criado_em,
            atualizado_em=model.atualizado_em
        )

    def _to_model(self, usuario: Usuario) -> UsuarioModel:
        """Converte entidade de domínio para model do SQLAlchemy"""
        return UsuarioModel(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            password_hash=usuario.password_hash
        )

    async def create(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário"""
        try:
            model = self._to_model(usuario)
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao criar usuário: {str(e)}", e)

    async def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        """Busca usuário por ID"""
        try:
            stmt = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar usuário: {str(e)}", e)

    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email"""
        try:
            stmt = select(UsuarioModel).where(UsuarioModel.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)
        except Exception as e:
            raise DatabaseException(f"Erro ao buscar usuário por email: {str(e)}", e)

    async def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
        nome: Optional[str] = None
    ) -> List[Usuario]:
        """Lista usuários com filtros opcionais"""
        try:
            stmt = select(UsuarioModel)

            # Aplicar filtros
            if nome:
                stmt = stmt.where(UsuarioModel.nome.ilike(f"%{nome}%"))

            # Ordenar por nome
            stmt = stmt.order_by(UsuarioModel.nome)

            # Paginação
            stmt = stmt.limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise DatabaseException(f"Erro ao listar usuários: {str(e)}", e)

    async def update(self, usuario_id: int, usuario: Usuario) -> Optional[Usuario]:
        """Atualiza um usuário"""
        try:
            stmt = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            # Atualizar campos
            model.nome = usuario.nome
            model.email = usuario.email
            if usuario.password_hash:
                model.password_hash = usuario.password_hash
            model.atualizado_em = datetime.now(timezone.utc)

            await self.session.commit()
            await self.session.refresh(model)

            return self._to_domain(model)
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao atualizar usuário: {str(e)}", e)

    async def delete(self, usuario_id: int) -> bool:
        """Remove um usuário"""
        try:
            stmt = select(UsuarioModel).where(UsuarioModel.id == usuario_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return False

            await self.session.delete(model)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Erro ao deletar usuário: {str(e)}", e)

    async def count(self, nome: Optional[str] = None) -> int:
        """Conta total de usuários com filtros"""
        try:
            stmt = select(func.count(UsuarioModel.id))

            if nome:
                stmt = stmt.where(UsuarioModel.nome.ilike(f"%{nome}%"))

            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseException(f"Erro ao contar usuários: {str(e)}", e)
