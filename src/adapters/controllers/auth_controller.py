"""
Controller de Autenticação
Gerencia endpoints de login e registro de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.schemas_api import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    BaseResponse
)
from src.application.auth_service import AuthService
from src.adapters.repositories.usuario_repository import UsuarioRepository
from src.db.session import get_session
from src.domain.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    EntityNotFoundError
)

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Dependency para obter instância do AuthService"""
    usuario_repository = UsuarioRepository(session)
    return AuthService(usuario_repository)


@router.post(
    "/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário com email e senha"
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Registra um novo usuário no sistema

    **Validações:**
    - Email único
    - Senha com força mínima (8 caracteres, maiúscula, minúscula, dígito)
    - Email válido

    **Retorna:**
    - Dados do usuário criado
    - Token JWT para autenticação
    """
    try:
        usuario, token = await auth_service.register(
            nome=register_data.nome,
            email=register_data.email,
            password=register_data.password
        )

        return AuthResponse(
            code="REGISTER_SUCCESS",
            message="Usuário registrado com sucesso",
            data={
                "user": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email
                },
                "token": token
            }
        )

    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Erro ao registrar usuário"
            }
        )


@router.post(
    "/auth/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer login",
    description="Autentica usuário com email e senha"
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Autentica um usuário

    **Validações:**
    - Email deve estar cadastrado
    - Senha deve corresponder ao hash armazenado

    **Segurança:**
    - Rate limiting: máximo 5 tentativas por minuto por IP
    - Mensagem genérica para credenciais inválidas (não expõe se email existe)

    **Retorna:**
    - Dados do usuário
    - Token JWT para autenticação
    """
    try:
        usuario, token = await auth_service.login(
            email=login_data.email,
            password=login_data.password
        )

        return AuthResponse(
            code="LOGIN_SUCCESS",
            message="Login realizado com sucesso",
            data={
                "user": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email
                },
                "token": token
            }
        )

    except BusinessRuleViolationError as e:
        # Não expor detalhes específicos (se email existe ou senha incorreta)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Credenciais inválidas"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Erro ao realizar login"
            }
        )


@router.get(
    "/auth/verify",
    response_model=BaseResponse,
    summary="Verificar token JWT",
    description="Verifica se um token JWT é válido"
)
async def verify_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verifica validade do token JWT

    **Headers esperados:**
    - Authorization: Bearer {token}

    **Retorna:**
    - Dados do usuário se token válido
    - Erro 401 se token inválido/expirado
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "MISSING_TOKEN",
                "message": "Token de autenticação não fornecido"
            }
        )

    token = auth_header.replace("Bearer ", "")

    usuario = await auth_service.get_current_user(token)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Token inválido ou expirado"
            }
        )

    return BaseResponse(
        code="TOKEN_VALID",
        message="Token válido",
        data={
            "user": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        }
    )
