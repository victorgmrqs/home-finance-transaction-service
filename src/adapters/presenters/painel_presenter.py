"""
Presenters para Painel
"""

from src.domain.models.painel import Painel


def present_painel_created(painel: Painel) -> dict:
    """Apresenta painel criado"""
    return {
        "code": "PAINEL_CREATED",
        "message": "Painel criado com sucesso",
        "data": {
            "id": painel.id,
            "nome": painel.nome,
            "descricao": painel.descricao,
            "tipo_conta": painel.tipo_conta,
            "usuario_id": painel.usuario_id,
            "criado_em": painel.criado_em.isoformat() if painel.criado_em else None,
            "atualizado_em": painel.atualizado_em.isoformat() if painel.atualizado_em else None
        }
    }


def present_painel_detail(painel: Painel) -> dict:
    """Apresenta detalhes do painel"""
    return {
        "code": "PAINEL_DETAIL_SUCCESS",
        "message": "Painel encontrado",
        "data": {
            "id": painel.id,
            "nome": painel.nome,
            "descricao": painel.descricao,
            "tipo_conta": painel.tipo_conta,
            "usuario_id": painel.usuario_id,
            "criado_em": painel.criado_em.isoformat() if painel.criado_em else None,
            "atualizado_em": painel.atualizado_em.isoformat() if painel.atualizado_em else None
        }
    }


def present_painel_list(paineis: list[Painel], total: int) -> dict:
    """Apresenta lista de painéis"""
    return {
        "code": "PAINEL_LIST_SUCCESS",
        "message": f"Encontrados {total} painéis",
        "data": [
            {
                "id": painel.id,
                "nome": painel.nome,
                "descricao": painel.descricao,
                "tipo_conta": painel.tipo_conta,
                "usuario_id": painel.usuario_id,
                "criado_em": painel.criado_em.isoformat() if painel.criado_em else None,
                "atualizado_em": painel.atualizado_em.isoformat() if painel.atualizado_em else None
            }
            for painel in paineis
        ],
        "total": total
    }


def present_painel_updated(painel: Painel) -> dict:
    """Apresenta painel atualizado"""
    return {
        "code": "PAINEL_UPDATED",
        "message": "Painel atualizado com sucesso",
        "data": {
            "id": painel.id,
            "nome": painel.nome,
            "descricao": painel.descricao,
            "tipo_conta": painel.tipo_conta,
            "usuario_id": painel.usuario_id,
            "criado_em": painel.criado_em.isoformat() if painel.criado_em else None,
            "atualizado_em": painel.atualizado_em.isoformat() if painel.atualizado_em else None
        }
    }


def present_painel_deleted(painel_id: int) -> dict:
    """Apresenta painel deletado"""
    return {
        "code": "PAINEL_DELETED",
        "message": "Painel deletado com sucesso",
        "data": None
    }
