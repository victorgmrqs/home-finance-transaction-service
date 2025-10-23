"""
Local Controller
Endpoints HTTP para gerenciamento de locais
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.adapters.repositories.local_repository import LocalRepository
from src.application.local_service import LocalService
from src.adapters.presenters.local_presenter import (
    present_local_created,
    present_local_detail,
    present_local_list,
    present_local_updated,
    present_local_deleted
)
from src.core.schemas_api import (
    LocalCreateRequest, 
    LocalUpdateRequest,
    LocalCreateResponse,
    LocalDetailResponse,
    LocalListResponse,
    LocalUpdateResponse,
    LocalDeleteResponse
)
from src.domain.models.local import Local

router = APIRouter(tags=["Locais"])


@router.post("/locais", status_code=status.HTTP_201_CREATED, response_model=LocalCreateResponse)
async def create_local(
    request: LocalCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo local

    Conforme ADR-002, permite registro incremental:
    - Pode criar com apenas nome_fantasia OU cnpj
    - Dados podem ser completados posteriormente

    - **nome_fantasia**: (Opcional) Nome fantasia do estabelecimento
    - **cnpj**: (Opcional) CNPJ (com ou sem formatação)
    - **razao_social**: (Opcional) Razão social
    - **categoria**: (Opcional) Categoria (ex: supermercado, farmácia)
    - **endereco**: (Opcional) Endereço
    """
    # Converter request para entidade de domínio
    local = Local(
        id=None,
        nome_fantasia=request.nome_fantasia,
        cnpj=request.cnpj,
        razao_social=request.razao_social,
        categoria=request.categoria,
        endereco=request.endereco
    )

    # Executar caso de uso
    repository = LocalRepository(session)
    service = LocalService(repository)
    created = await service.create_local(local)

    return present_local_created(created)


@router.get("/locais", response_model=LocalListResponse)
async def list_locais(
    limit: int = Query(100, ge=1, le=500, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista todos os locais

    Parâmetros de query:
    - **limit**: Limite de resultados (padrão: 100, máx: 500)
    - **offset**: Offset para paginação (padrão: 0)
    """
    repository = LocalRepository(session)
    service = LocalService(repository)

    locais, total = await service.list_locais(limit=limit, offset=offset)

    return present_local_list(locais, total)


@router.get("/locais/{id}", response_model=LocalDetailResponse)
async def get_local(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca um local por ID

    - **id**: ID do local
    """
    repository = LocalRepository(session)
    service = LocalService(repository)
    local = await service.get_local(id)

    return present_local_detail(local)


@router.put("/locais/{id}", response_model=LocalUpdateResponse)
async def update_local(
    id: int,
    request: LocalUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza um local existente

    Permite completar dados de locais incompletos (ADR-002)

    - **id**: ID do local a atualizar
    - Campos no body: mesmos da criação (todos opcionais)
    """
    repository = LocalRepository(session)
    service = LocalService(repository)

    # Buscar local atual
    current = await service.get_local(id)

    # Aplicar updates (manter valores atuais se não fornecidos)
    updated_local = Local(
        id=current.id,
        nome_fantasia=request.nome_fantasia if request.nome_fantasia else current.nome_fantasia,
        cnpj=request.cnpj if request.cnpj else current.cnpj,
        razao_social=request.razao_social if request.razao_social else current.razao_social,
        categoria=request.categoria if request.categoria else current.categoria,
        endereco=request.endereco if request.endereco else current.endereco
    )

    updated = await service.update_local(id, updated_local)

    return present_local_updated(updated)


@router.delete("/locais/{id}", status_code=status.HTTP_200_OK, response_model=LocalDeleteResponse)
async def delete_local(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um local

    Nota: Transações vinculadas terão local_id setado para NULL

    - **id**: ID do local a remover
    """
    repository = LocalRepository(session)
    service = LocalService(repository)
    await service.delete_local(id)

    return present_local_deleted()
