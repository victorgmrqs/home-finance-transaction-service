"""
Painel Controller
Endpoints HTTP para CRUD de painéis
"""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.db.session import get_session
from src.adapters.repositories.painel_repository import PainelRepository
from src.application.painel_service import PainelService
from src.adapters.presenters.painel_presenter import (
    present_painel_created,
    present_painel_detail,
    present_painel_list,
    present_painel_updated,
    present_painel_deleted
)
from src.core.schemas_api import (
    PainelCreateRequest, 
    PainelUpdateRequest,
    PainelCreateResponse,
    PainelDetailResponse,
    PainelListResponse,
    PainelUpdateResponse,
    PainelDeleteResponse
)
from src.domain.models.painel import Painel
from src.domain.exceptions import DuplicatePainelException

router = APIRouter(tags=["Painéis"])


@router.post("/paineis", status_code=status.HTTP_201_CREATED, response_model=PainelCreateResponse)
async def create_painel(
    request: PainelCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo painel

    - **nome**: Nome do painel (obrigatório)
    - **descricao**: Descrição do painel (opcional)
    - **tipo_conta**: Tipo de conta (CARTAO_CREDITO, CONTA_BANCARIA, DINHEIRO)
    - **usuario_id**: ID do usuário proprietário (obrigatório)
    """
    try:
        # Converter request para entidade de domínio
        painel = Painel(
            id=None,
            nome=request.nome,
            descricao=request.descricao,
            tipo_conta=request.tipo_conta,
            usuario_id=request.usuario_id
        )

        # Executar caso de uso
        repository = PainelRepository(session)
        service = PainelService(repository)
        created = await service.create_painel(painel)

        return present_painel_created(created)
    except DuplicatePainelException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DATABASE_ERROR",
                "message": e.message,
                "data": None
            }
        )


@router.get("/paineis", response_model=PainelListResponse)
async def list_painels(
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuário"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista painéis com filtros opcionais

    Parâmetros de query:
    - **limit**: Limite de resultados (padrão: 10, máx: 100)
    - **offset**: Offset para paginação (padrão: 0)
    - **usuario_id**: Filtrar por usuário
    - **nome**: Filtrar por nome
    """
    repository = PainelRepository(session)
    service = PainelService(repository)

    paineis, total = await service.list_paineis(
        limit=limit,
        offset=offset,
        usuario_id=usuario_id,
        nome=nome
    )

    return present_painel_list(paineis, total)


@router.get("/usuarios/{usuario_id}/paineis", response_model=PainelListResponse)
async def list_painels_by_usuario(
    usuario_id: int,
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista painéis de um usuário específico

    Parâmetros de query:
    - **limit**: Limite de resultados (padrão: 10, máx: 100)
    - **offset**: Offset para paginação (padrão: 0)
    - **nome**: Filtrar por nome
    """
    repository = PainelRepository(session)
    service = PainelService(repository)

    paineis, total = await service.list_paineis_by_usuario(
        usuario_id=usuario_id,
        limit=limit,
        offset=offset,
        nome=nome
    )

    return present_painel_list(paineis, total)


@router.get("/paineis/{id}", response_model=PainelDetailResponse)
async def get_painel(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca um painel por ID

    - **id**: ID do painel
    """
    repository = PainelRepository(session)
    service = PainelService(repository)
    painel = await service.get_painel(id)

    if painel is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": "Painel não encontrado",
                "data": None
            }
        )

    return present_painel_detail(painel)


@router.put("/paineis/{id}", response_model=PainelUpdateResponse)
async def update_painel(
    id: int,
    request: PainelUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza um painel existente

    - **id**: ID do painel a atualizar
    - Campos no body: mesmos da criação (todos opcionais)
    """
    repository = PainelRepository(session)
    service = PainelService(repository)

    # Buscar painel atual
    current = await service.get_painel(id)
    if current is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": "Painel não encontrado",
                "data": None
            }
        )

    # Aplicar updates (manter valores atuais se não fornecidos)
    updated_painel = Painel(
        id=current.id,
        nome=request.nome if request.nome else current.nome,
        descricao=request.descricao if request.descricao is not None else current.descricao,
        tipo_conta=request.tipo_conta if request.tipo_conta else current.tipo_conta,
        usuario_id=current.usuario_id  # Não permite alterar usuário
    )

    updated = await service.update_painel(id, updated_painel)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": "Painel não encontrado",
                "data": None
            }
        )

    return present_painel_updated(updated)


@router.delete("/paineis/{id}", status_code=status.HTTP_200_OK, response_model=PainelDeleteResponse)
async def delete_painel(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um painel

    - **id**: ID do painel a remover
    """
    repository = PainelRepository(session)
    service = PainelService(repository)
    deleted = await service.delete_painel(id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": "Painel não encontrado",
                "data": None
            }
        )

    return present_painel_deleted(id)
