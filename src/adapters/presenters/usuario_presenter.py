"""
Presenters para Usuario
"""

from src.domain.models.usuario import Usuario


def present_usuario_created(usuario: Usuario) -> dict:
    """Apresenta usuário criado"""
    return {
        "code": "USUARIO_CREATED",
        "message": "Usuário criado com sucesso",
        "data": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
            "atualizado_em": usuario.atualizado_em.isoformat() if usuario.atualizado_em else None
        }
    }


def present_usuario_detail(usuario: Usuario) -> dict:
    """Apresenta detalhes do usuário"""
    return {
        "code": "USUARIO_DETAIL_SUCCESS",
        "message": "Usuário encontrado",
        "data": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
            "atualizado_em": usuario.atualizado_em.isoformat() if usuario.atualizado_em else None
        }
    }


def present_usuario_list(usuarios: list[Usuario], total: int) -> dict:
    """Apresenta lista de usuários"""
    return {
        "code": "USUARIO_LIST_SUCCESS",
        "message": f"Encontrados {total} usuários",
        "data": [
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
                "atualizado_em": usuario.atualizado_em.isoformat() if usuario.atualizado_em else None
            }
            for usuario in usuarios
        ],
        "total": total
    }


def present_usuario_updated(usuario: Usuario) -> dict:
    """Apresenta usuário atualizado"""
    return {
        "code": "USUARIO_UPDATED",
        "message": "Usuário atualizado com sucesso",
        "data": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None,
            "atualizado_em": usuario.atualizado_em.isoformat() if usuario.atualizado_em else None
        }
    }


def present_usuario_deleted(usuario_id: int) -> dict:
    """Apresenta usuário deletado"""
    return {
        "code": "USUARIO_DELETED",
        "message": "Usuário deletado com sucesso",
        "data": None
    }
