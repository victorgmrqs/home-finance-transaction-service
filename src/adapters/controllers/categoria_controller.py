"""
Categoria Controller
Endpoints HTTP para gerenciamento de categorias
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.adapters.repositories.categoria_repository import CategoriaRepository
from src.application.categoria_service import CategoriaService
from src.adapters.presenters.categoria_presenter import (
    present_categoria_created,
    present_categoria_detail,
    present_categoria_list,
    present_categoria_updated,
    present_categoria_deleted
)
from src.core.schemas_api import (
    CategoriaCreateRequest, 
    CategoriaUpdateRequest,
    CategoriaCreateResponse,
    CategoriaDetailResponse,
    CategoriaListResponse,
    CategoriaUpdateResponse,
    CategoriaDeleteResponse
)
from src.domain.models.categoria import Categoria
from src.domain.exceptions import DatabaseException

router = APIRouter(tags=["Categorias"])


@router.get("/categorias", response_model=CategoriaListResponse)
async def list_categorias(
    session: AsyncSession = Depends(get_session)
):
    """
    Lista todas as categorias disponíveis para o usuário autenticado.
    
    Retorna:
    - Categorias padrão do sistema (is_default=true, usuario_id=null)
    - Categorias customizadas do usuário (is_default=false, usuario_id=X)
    
    TODO: Implementar autenticação para obter usuario_id do token JWT
    """
    # TODO: Obter usuario_id do token JWT quando autenticação estiver implementada
    # Por enquanto, usando usuario_id=1 como exemplo
    usuario_id = 1
    
    repository = CategoriaRepository(session)
    service = CategoriaService(repository)
    
    categorias = await service.list_categorias_for_user(usuario_id)
    
    return present_categoria_list(categorias)


@router.post("/categorias", status_code=status.HTTP_201_CREATED, response_model=CategoriaCreateResponse)
async def create_categoria(
    request: CategoriaCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria uma nova categoria customizada para o usuário autenticado.
    
    Validações:
    - Nome único por usuário
    - Nome obrigatório (max 100 caracteres)
    
    TODO: Implementar autenticação para obter usuario_id do token JWT
    """
    # TODO: Obter usuario_id do token JWT quando autenticação estiver implementada
    # Por enquanto, usando usuario_id=1 como exemplo
    usuario_id = 1
    
    # Converter request para entidade de domínio
    categoria = Categoria(
        id=None,
        nome=request.nome,
        descricao=request.descricao,
        usuario_id=usuario_id,
        is_default=False
    )
    
    # Executar caso de uso
    repository = CategoriaRepository(session)
    service = CategoriaService(repository)
    
    try:
        created = await service.create_categoria(categoria)
        return present_categoria_created(created)
    except DatabaseException as e:
        if "já existe" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categorias/{id}", response_model=CategoriaDetailResponse)
async def get_categoria(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca uma categoria específica por ID
    
    - **id**: ID da categoria
    """
    repository = CategoriaRepository(session)
    service = CategoriaService(repository)
    categoria = await service.get_categoria(id)
    
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    return present_categoria_detail(categoria)


@router.put("/categorias/{id}", response_model=CategoriaUpdateResponse)
async def update_categoria(
    id: int,
    request: CategoriaUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza uma categoria customizada do usuário.
    
    Restrições:
    - Apenas categorias customizadas (is_default=false)
    - Apenas categorias do próprio usuário
    
    TODO: Implementar autenticação para obter usuario_id do token JWT
    """
    # TODO: Obter usuario_id do token JWT quando autenticação estiver implementada
    # Por enquanto, usando usuario_id=1 como exemplo
    usuario_id = 1
    
    repository = CategoriaRepository(session)
    service = CategoriaService(repository)
    
    # Buscar categoria atual
    current = await service.get_categoria(id)
    if current is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Aplicar updates (manter valores atuais se não fornecidos)
    updated_categoria = Categoria(
        id=current.id,
        nome=request.nome if request.nome else current.nome,
        descricao=request.descricao if request.descricao is not None else current.descricao,
        usuario_id=current.usuario_id,
        is_default=current.is_default,
        criado_em=current.criado_em,
        atualizado_em=current.atualizado_em
    )
    
    try:
        updated = await service.update_categoria(id, updated_categoria, usuario_id)
        
        if updated is None:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        return present_categoria_updated(updated)
    except DatabaseException as e:
        if "não é possível editar categorias padrão" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        elif "não tem permissão" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        elif "já existe" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/categorias/{id}", status_code=status.HTTP_200_OK, response_model=CategoriaDeleteResponse)
async def delete_categoria(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Deleta uma categoria customizada do usuário.
    
    Restrições:
    - Apenas categorias customizadas (is_default=false)
    - Apenas categorias do próprio usuário
    - Não deleta se existirem transações associadas
    
    TODO: Implementar autenticação para obter usuario_id do token JWT
    """
    # TODO: Obter usuario_id do token JWT quando autenticação estiver implementada
    # Por enquanto, usando usuario_id=1 como exemplo
    usuario_id = 1
    
    repository = CategoriaRepository(session)
    service = CategoriaService(repository)
    
    try:
        deleted = await service.delete_categoria(id, usuario_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        return present_categoria_deleted(id)
    except DatabaseException as e:
        if "não é possível deletar categorias padrão" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        elif "não tem permissão" in str(e).lower():
            raise HTTPException(status_code=403, detail=str(e))
        elif "transações associadas" in str(e).lower():
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))






