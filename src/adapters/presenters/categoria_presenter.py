"""
Categoria Presenter
Formatadores de resposta para endpoints de categorias
"""

from src.core.schemas_api import (
    CategoriaCreateResponse,
    CategoriaDetailResponse,
    CategoriaListResponse,
    CategoriaUpdateResponse,
    CategoriaDeleteResponse,
    CategoriaResponse
)
from src.domain.models.categoria import Categoria


def present_categoria_response(categoria: Categoria) -> CategoriaResponse:
    """Converte entidade de domínio para schema de resposta"""
    return CategoriaResponse(
        id=categoria.id,
        nome=categoria.nome,
        descricao=categoria.descricao,
        usuario_id=categoria.usuario_id,
        is_default=categoria.is_default,
        criado_em=categoria.criado_em.isoformat() if categoria.criado_em else "",
        atualizado_em=categoria.atualizado_em.isoformat() if categoria.atualizado_em else ""
    )


def present_categoria_created(categoria: Categoria) -> CategoriaCreateResponse:
    """Formata resposta de criação de categoria"""
    return CategoriaCreateResponse(
        code="CREATED",
        message="Categoria criada com sucesso",
        data=present_categoria_response(categoria)
    )


def present_categoria_detail(categoria: Categoria) -> CategoriaDetailResponse:
    """Formata resposta de detalhe de categoria"""
    return CategoriaDetailResponse(
        code="SUCCESS",
        message="Categoria encontrada",
        data=present_categoria_response(categoria)
    )


def present_categoria_list(categorias: list[Categoria]) -> CategoriaListResponse:
    """Formata resposta de lista de categorias"""
    return CategoriaListResponse(
        code="SUCCESS",
        message="Categorias listadas com sucesso",
        data=[present_categoria_response(categoria) for categoria in categorias]
    )


def present_categoria_updated(categoria: Categoria) -> CategoriaUpdateResponse:
    """Formata resposta de atualização de categoria"""
    return CategoriaUpdateResponse(
        code="SUCCESS",
        message="Categoria atualizada com sucesso",
        data=present_categoria_response(categoria)
    )


def present_categoria_deleted(categoria_id: int) -> CategoriaDeleteResponse:
    """Formata resposta de exclusão de categoria"""
    return CategoriaDeleteResponse(
        code="SUCCESS",
        message="Categoria deletada com sucesso",
        data=None
    )






