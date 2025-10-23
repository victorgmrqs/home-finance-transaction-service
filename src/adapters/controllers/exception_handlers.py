"""
Exception Handlers para FastAPI
Define como cada tipo de exceção será tratada e retornada como resposta HTTP
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError

from src.domain.exceptions import (
    DomainException,
    ValidationException,
    TransactionNotFoundException,
    LocalNotFoundException,
    InvalidTransactionException,
    InvalidLocalException,
    DatabaseException,
    DuplicateCNPJException
)
from src.shared.responses import error_response


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handler genérico para exceções de domínio"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(
            code=exc.code,
            message=exc.message,
            data=None
        )
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handler para erros de validação de domínio"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            code=exc.code,
            message=exc.message,
            data=None
        )
    )


async def not_found_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handler para entidades não encontradas"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response(
            code=exc.code,
            message=exc.message,
            data=None
        )
    )


async def duplicate_cnpj_exception_handler(request: Request, exc: DuplicateCNPJException) -> JSONResponse:
    """Handler para CNPJ duplicado"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response(
            code=exc.code,
            message=exc.message,
            data={"cnpj": exc.cnpj}
        )
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """Handler para erros de banco de dados"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code="DATABASE_ERROR",
            message="Erro ao acessar o banco de dados",
            data=None
        )
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handler para erros de integridade do SQLAlchemy"""
    # Tentar identificar se é CNPJ duplicado
    error_msg = str(exc.orig)

    if "cnpj" in error_msg.lower() and "unique" in error_msg.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(
                code="DUPLICATE_CNPJ",
                message="CNPJ já cadastrado no sistema",
                data=None
            )
        )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_response(
            code="INTEGRITY_ERROR",
            message="Violação de integridade de dados",
            data=None
        )
    )


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler para erros de validação do Pydantic/FastAPI"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            code="VALIDATION_ERROR",
            message="Erro de validação nos dados enviados",
            data={"errors": errors}
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler para HTTPException do FastAPI"""
    # Se o detail é um dicionário com as chaves esperadas, usar diretamente
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # Caso contrário, retornar o detail diretamente (compatibilidade com testes existentes)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler genérico para exceções não tratadas"""
    # Log do erro para debugging (em produção, usar sistema de logging apropriado)
    import traceback
    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message="Erro interno do servidor",
            data=None
        )
    )


def register_exception_handlers(app):
    """
    Registra todos os exception handlers na aplicação FastAPI

    Deve ser chamado no main.py após criar a instância do FastAPI
    """
    # Exceções de domínio
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(TransactionNotFoundException, not_found_exception_handler)
    app.add_exception_handler(LocalNotFoundException, not_found_exception_handler)
    app.add_exception_handler(InvalidTransactionException, domain_exception_handler)
    app.add_exception_handler(InvalidLocalException, domain_exception_handler)
    app.add_exception_handler(DuplicateCNPJException, duplicate_cnpj_exception_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)

    # Exceções de infraestrutura
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # Exceções do FastAPI
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Exceção genérica (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
