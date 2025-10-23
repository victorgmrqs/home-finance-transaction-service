"""
Respostas padronizadas da aplicação
Segue o padrão definido no contrato da API (transaction-service-contract.yaml)
"""

from typing import Any, Optional


def success_response(
    code: str,
    message: str,
    data: Optional[Any] = None
) -> dict:
    """
    Resposta de sucesso padronizada

    Formato:
    {
        "code": "ENDPOINT_SPECIFIC_CODE",
        "message": "Mensagem de status",
        "data": { ... } ou null
    }
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def error_response(
    code: str,
    message: str,
    data: Optional[Any] = None
) -> dict:
    """
    Resposta de erro padronizada

    Formato:
    {
        "code": "ERROR_CODE",
        "message": "Mensagem de erro",
        "data": null
    }
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }