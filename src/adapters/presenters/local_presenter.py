"""
Local Presenter
Formatação de responses para endpoints de locais
"""


from src.domain.models.local import Local
from src.shared.responses import success_response


def present_local(local: Local) -> dict:
    """
    Apresenta um local como resposta da API

    Args:
        local: Entidade de local

    Returns:
        dict: Response formatado conforme contrato
    """
    return {
        "id": local.id,
        "nome_fantasia": local.nome_fantasia,
        "cnpj": local.cnpj,
        "razao_social": local.razao_social,
        "categoria": local.categoria,
        "endereco": local.endereco,
        "criado_em": local.criado_em.isoformat(),
        "atualizado_em": local.atualizado_em.isoformat()
    }


def present_local_created(local: Local) -> dict:
    """Apresenta resposta de local criado"""
    return success_response(
        code="LOCAL_CREATED",
        message="Local criado com sucesso",
        data=present_local(local)
    )


def present_local_detail(local: Local) -> dict:
    """Apresenta resposta de detalhe de local"""
    return success_response(
        code="LOCAL_DETAIL_SUCCESS",
        message="Local encontrado",
        data=present_local(local)
    )


def present_local_list(locais: list[Local], total: int) -> dict:
    """
    Apresenta lista de locais

    Args:
        locais: Lista de locais
        total: Total de registros

    Returns:
        dict: Response formatado com lista
    """
    return success_response(
        code="LOCAL_LIST_SUCCESS",
        message="Lista de locais obtida com sucesso",
        data=[present_local(local) for local in locais]
    )


def present_local_updated(local: Local) -> dict:
    """Apresenta resposta de local atualizado"""
    return success_response(
        code="LOCAL_UPDATED",
        message="Local atualizado com sucesso",
        data=present_local(local)
    )


def present_local_deleted() -> dict:
    """Apresenta resposta de local deletado"""
    return success_response(
        code="LOCAL_DELETED",
        message="Local removido com sucesso",
        data=None
    )
