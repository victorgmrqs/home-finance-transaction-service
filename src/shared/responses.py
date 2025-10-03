"""
Respostas padronizadas da aplicação
"""

from datetime import datetime
from typing import Any, Optional


def success_response(
    code: str,
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> dict:
    """Resposta de sucesso padronizada"""
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(
    code: str,
    message: str,
    details: Optional[list] = None,
    status_code: int = 400
) -> dict:
    """Resposta de erro padronizada"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "details": details or [],
        "timestamp": datetime.utcnow().isoformat()
    }