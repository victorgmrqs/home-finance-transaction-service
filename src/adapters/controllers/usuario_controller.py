"""
Usuario Controller
Endpoints HTTP para gerenciamento de usuários
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.presenters.usuario_presenter import (
    present_usuario_created,
    present_usuario_deleted,
    present_usuario_detail,
    present_usuario_list,
    present_usuario_updated,
)
from src.adapters.repositories.usuario_repository import UsuarioRepository
from src.application.usuario_service import UsuarioService
from src.core.schemas_api import (
    UsuarioCreateRequest,
    UsuarioCreateResponse,
    UsuarioDeleteResponse,
    UsuarioDetailResponse,
    UsuarioListResponse,
    UsuarioUpdateRequest,
    UsuarioUpdateResponse,
)
from src.db.session import get_session
from src.domain.exceptions import DatabaseException
from src.domain.models.usuario import Usuario

router = APIRouter(tags=["Usuários"])
logger = logging.getLogger(__name__)


@router.post("/usuarios", status_code=status.HTTP_201_CREATED, response_model=UsuarioCreateResponse)
async def create_usuario(
    request: UsuarioCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo usuário

    - **nome**: Nome do usuário (obrigatório)
    - **email**: Email do usuário (opcional)
    """
    try:
        # Converter request para entidade de domínio
        usuario = Usuario(
            id=None,
            nome=request.nome,
            email=request.email
        )

        # Executar caso de uso
        repository = UsuarioRepository(session)
        service = UsuarioService(repository)
        created = await service.create_usuario(usuario)

        return present_usuario_created(created)
    except DatabaseException as e:
        # Log da exceção para rastreabilidade
        logger.error(f"Erro de banco de dados ao criar usuário: {e}", exc_info=True)

        # Verificar se é erro de email duplicado
        error_msg = str(e).lower()
        if "unique" in error_msg and "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado no sistema"
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except IntegrityError as e:
        # Log da exceção para rastreabilidade
        logger.error(f"Erro de integridade ao criar usuário: {e}", exc_info=True)

        # Verificar se é erro de email duplicado
        error_msg = str(e.orig).lower()
        if "unique" in error_msg and "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado no sistema"
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro de integridade de dados"
        ) from e


@router.get("/usuarios", response_model=UsuarioListResponse)
async def list_usuarios(
    limit: int = Query(10, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    nome: str | None = Query(None, description="Filtrar por nome"),
    session: AsyncSession = Depends(get_session)
):
    """
    Lista usuários com filtros opcionais

    Parâmetros de query:
    - **limit**: Limite de resultados (padrão: 10, máx: 100)
    - **offset**: Offset para paginação (padrão: 0)
    - **nome**: Filtrar por nome
    """
    try:
        repository = UsuarioRepository(session)
        service = UsuarioService(repository)

        usuarios, total = await service.list_usuarios(
            limit=limit,
            offset=offset,
            nome=nome
        )

        return present_usuario_list(usuarios, total)
    except DatabaseException as e:
        # Log da exceção para rastreabilidade
        logger.error(f"Erro de banco de dados ao listar usuários: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao acessar o banco de dados"
        ) from e


@router.get("/usuarios/{id}", response_model=UsuarioDetailResponse)
async def get_usuario(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca um usuário por ID

    - **id**: ID do usuário
    """
    repository = UsuarioRepository(session)
    service = UsuarioService(repository)
    usuario = await service.get_usuario(id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return present_usuario_detail(usuario)


@router.get("/usuarios/email/{email}", response_model=UsuarioDetailResponse)
async def get_usuario_by_email(
    email: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca um usuário por email

    - **email**: Email do usuário
    """
    try:
        repository = UsuarioRepository(session)
        service = UsuarioService(repository)
        usuario = await service.get_usuario_by_email(email)

        if usuario is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return present_usuario_detail(usuario)
    except DatabaseException as e:
        # Log da exceção para rastreabilidade
        logger.error(f"Erro de banco de dados ao buscar usuário por email: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao acessar o banco de dados"
        ) from e


@router.put("/usuarios/{id}", response_model=UsuarioUpdateResponse)
async def update_usuario(
    id: int,
    request: UsuarioUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza um usuário existente

    - **id**: ID do usuário a atualizar
    - Campos no body: mesmos da criação (todos opcionais)
    """
    repository = UsuarioRepository(session)
    service = UsuarioService(repository)

    # Buscar usuário atual
    current = await service.get_usuario(id)
    if current is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Aplicar updates (manter valores atuais se não fornecidos)
    updated_usuario = Usuario(
        id=current.id,
        nome=request.nome if request.nome else current.nome,
        email=request.email if request.email is not None else current.email
    )

    updated = await service.update_usuario(id, updated_usuario)

    if updated is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return present_usuario_updated(updated)


@router.delete("/usuarios/{id}", status_code=status.HTTP_200_OK, response_model=UsuarioDeleteResponse)
async def delete_usuario(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um usuário

    - **id**: ID do usuário a remover
    """
    repository = UsuarioRepository(session)
    service = UsuarioService(repository)
    deleted = await service.delete_usuario(id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return present_usuario_deleted(id)
