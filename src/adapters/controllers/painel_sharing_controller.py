"""
Painel Sharing Controller
Endpoints HTTP para compartilhamento de painéis
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.middlewares.auth_middleware import get_current_user_id
from src.adapters.repositories.models import PainelUsuarioModel
from src.adapters.repositories.painel_repository import PainelRepository
from src.core.schemas_api import CompartilhamentoPainelRequest, CompartilhamentoPainelUpdateRequest
from src.db.session import get_session
from src.shared.responses import success_response

router = APIRouter(tags=["Painéis - Compartilhamento"])


@router.post("/paineis/{id}/compartilhar", status_code=status.HTTP_201_CREATED)
async def compartilhar_painel(
    request: Request,
    id: int,
    compartilhamento: CompartilhamentoPainelRequest,
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Compartilha um painel com outro usuário

    **Requer autenticação** (header X-User-ID em dev)

    Body:
    - **usuario_id**: ID do usuário para compartilhar
    - **tipo_permissao**: OWNER, EDITOR ou VIEWER
    """
    # Verificar se o painel existe
    painel_repository = PainelRepository(session)
    painel = await painel_repository.get_by_id(id)
    if not painel:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": "Painel não encontrado",
                "data": None
            }
        )

    # Verificar se já existe compartilhamento
    stmt = select(PainelUsuarioModel).where(
        PainelUsuarioModel.painel_id == id,
        PainelUsuarioModel.usuario_id == compartilhamento.usuario_id
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "COMPARTILHAMENTO_JA_EXISTE",
                "message": "Painel já está compartilhado com este usuário",
                "data": None
            }
        )

    # Criar compartilhamento
    novo_compartilhamento = PainelUsuarioModel(
        painel_id=id,
        usuario_id=compartilhamento.usuario_id,
        tipo_permissao=compartilhamento.tipo_permissao
    )

    session.add(novo_compartilhamento)
    await session.commit()
    await session.refresh(novo_compartilhamento)

    return success_response(
        code="PAINEL_COMPARTILHADO",
        message="Painel compartilhado com sucesso",
        data={
            "id": novo_compartilhamento.id,
            "painel_id": novo_compartilhamento.painel_id,
            "usuario_id": novo_compartilhamento.usuario_id,
            "tipo_permissao": novo_compartilhamento.tipo_permissao,
            "criado_em": novo_compartilhamento.criado_em.isoformat(),
            "atualizado_em": novo_compartilhamento.atualizado_em.isoformat()
        }
    )


@router.get("/paineis/{id}/compartilhamentos")
async def listar_compartilhamentos(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Lista todos os compartilhamentos de um painel

    **Requer autenticação** (header X-User-ID em dev)
    """
    stmt = select(PainelUsuarioModel).where(PainelUsuarioModel.painel_id == id)
    result = await session.execute(stmt)
    compartilhamentos = result.scalars().all()

    data = [
        {
            "id": c.id,
            "painel_id": c.painel_id,
            "usuario_id": c.usuario_id,
            "tipo_permissao": c.tipo_permissao,
            "criado_em": c.criado_em.isoformat(),
            "atualizado_em": c.atualizado_em.isoformat()
        }
        for c in compartilhamentos
    ]

    return success_response(
        code="COMPARTILHAMENTOS_LISTADOS",
        message="Compartilhamentos listados com sucesso",
        data=data
    )


@router.put("/paineis/{painel_id}/compartilhamentos/{usuario_id}")
async def atualizar_compartilhamento(
    request: Request,
    painel_id: int,
    usuario_id: int,
    update: CompartilhamentoPainelUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Atualiza a permissão de compartilhamento

    **Requer autenticação** (header X-User-ID em dev)

    Body:
    - **tipo_permissao**: Nova permissão (OWNER, EDITOR ou VIEWER)
    """
    stmt = select(PainelUsuarioModel).where(
        PainelUsuarioModel.painel_id == painel_id,
        PainelUsuarioModel.usuario_id == usuario_id
    )
    result = await session.execute(stmt)
    compartilhamento = result.scalar_one_or_none()

    if not compartilhamento:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "COMPARTILHAMENTO_NOT_FOUND",
                "message": "Compartilhamento não encontrado",
                "data": None
            }
        )

    compartilhamento.tipo_permissao = update.tipo_permissao
    await session.commit()
    await session.refresh(compartilhamento)

    return success_response(
        code="COMPARTILHAMENTO_ATUALIZADO",
        message="Permissão atualizada com sucesso",
        data={
            "id": compartilhamento.id,
            "painel_id": compartilhamento.painel_id,
            "usuario_id": compartilhamento.usuario_id,
            "tipo_permissao": compartilhamento.tipo_permissao,
            "criado_em": compartilhamento.criado_em.isoformat(),
            "atualizado_em": compartilhamento.atualizado_em.isoformat()
        }
    )


@router.delete("/paineis/{painel_id}/compartilhamentos/{usuario_id}")
async def remover_compartilhamento(
    request: Request,
    painel_id: int,
    usuario_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Remove o compartilhamento de um painel

    **Requer autenticação** (header X-User-ID em dev)
    """
    stmt = select(PainelUsuarioModel).where(
        PainelUsuarioModel.painel_id == painel_id,
        PainelUsuarioModel.usuario_id == usuario_id
    )
    result = await session.execute(stmt)
    compartilhamento = result.scalar_one_or_none()

    if not compartilhamento:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "COMPARTILHAMENTO_NOT_FOUND",
                "message": "Compartilhamento não encontrado",
                "data": None
            }
        )

    await session.delete(compartilhamento)
    await session.commit()

    return success_response(
        code="COMPARTILHAMENTO_REMOVIDO",
        message="Compartilhamento removido com sucesso",
        data=None
    )
