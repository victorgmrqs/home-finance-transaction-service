"""
Controller de Autenticação
Gerencia endpoints de login e registro de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.usuario_repository import UsuarioRepository
from src.application.auth_service import AuthService
from src.core.config import settings
from src.core.schemas_api import (
    AuthDataResponseCookie,
    AuthResponseCookie,
    AuthUserResponse,
    BaseResponse,
    LoginRequest,
    RegisterRequest,
)
from src.db.session import get_session
from src.domain.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
)
from src.ports.usuario_port import UsuarioRepositoryPort

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Dependency para obter instância do AuthService"""
    usuario_repository: UsuarioRepositoryPort = UsuarioRepository(session)  # type: ignore[assignment]
    return AuthService(usuario_repository)


@router.post(
    "/auth/register",
    response_model=AuthResponseCookie,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário com email e senha. Token JWT é retornado via HttpOnly cookie."
)
@limiter.limit("5/minute")
async def register(
    response: Response,
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

    **Segurança:**
    - Token retornado via HttpOnly cookie (proteção contra XSS)

    **Retorna:**
    - Dados do usuário criado
    - Token JWT via Set-Cookie header (HttpOnly, Secure em prod, SameSite)
    """
    try:
        usuario, token = await auth_service.register(
            nome=register_data.nome,
            email=register_data.email,
            password=register_data.password
        )

        if usuario.id is None:
            raise ValueError("Usuário criado deve ter ID")
        if usuario.email is None:
            raise ValueError("Usuário criado deve ter email")

        # Configurar cookie com o token JWT
        response.set_cookie(
            key=settings.cookie_name,
            value=token,
            httponly=settings.cookie_httponly,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            max_age=settings.cookie_max_age,
            path="/"
        )

        return AuthResponseCookie(
            code="REGISTER_SUCCESS",
            message="Usuário registrado com sucesso",
            data=AuthDataResponseCookie(
                user=AuthUserResponse(
                    id=usuario.id,
                    nome=usuario.nome,
                    email=usuario.email
                )
            )
        )

    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        ) from e
    except DuplicateEntityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": str(e)
            }
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Erro ao registrar usuário"
            }
        ) from e


@router.post(
    "/auth/login",
    response_model=AuthResponseCookie,
    status_code=status.HTTP_200_OK,
    summary="Fazer login",
    description="Autentica usuário com email e senha. Token JWT é retornado via HttpOnly cookie."
)
@limiter.limit("5/minute")
async def login(
    response: Response,
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
    - Token retornado via HttpOnly cookie (proteção contra XSS)

    **Retorna:**
    - Dados do usuário
    - Token JWT via Set-Cookie header (HttpOnly, Secure em prod, SameSite)
    """
    try:
        usuario, token = await auth_service.login(
            email=login_data.email,
            password=login_data.password
        )

        if usuario.id is None:
            raise ValueError("Usuário autenticado deve ter ID")
        if usuario.email is None:
            raise ValueError("Usuário autenticado deve ter email")

        # Configurar cookie com o token JWT
        response.set_cookie(
            key=settings.cookie_name,
            value=token,
            httponly=settings.cookie_httponly,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
            max_age=settings.cookie_max_age,
            path="/"
        )

        return AuthResponseCookie(
            code="LOGIN_SUCCESS",
            message="Login realizado com sucesso",
            data=AuthDataResponseCookie(
                user=AuthUserResponse(
                    id=usuario.id,
                    nome=usuario.nome,
                    email=usuario.email
                )
            )
        )

    except BusinessRuleViolationError as e:
        # Não expor detalhes específicos (se email existe ou senha incorreta)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Credenciais inválidas"
            }
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Erro ao realizar login"
            }
        ) from e


@router.post(
    "/auth/logout",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer logout",
    description="Remove o cookie de autenticação"
)
async def logout(response: Response):
    """
    Remove o cookie de autenticação do usuário

    **Ação:**
    - Limpa o cookie HttpOnly definindo max_age=0

    **Retorna:**
    - Mensagem de sucesso
    """
    # Limpar cookie definindo max_age=0
    response.delete_cookie(
        key=settings.cookie_name,
        path="/"
    )

    return BaseResponse(
        code="LOGOUT_SUCCESS",
        message="Logout realizado com sucesso",
        data=None
    )


@router.get(
    "/auth/verify",
    response_model=BaseResponse,
    summary="Verificar token JWT",
    description="Verifica se um token JWT é válido (via cookie ou header Authorization)"
)
async def verify_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verifica validade do token JWT

    **Token pode vir de:**
    - Cookie HttpOnly (preferência)
    - Header Authorization: Bearer {token} (fallback)

    **Retorna:**
    - Dados do usuário se token válido
    - Erro 401 se token inválido/expirado
    """
    # Tentar ler do cookie primeiro
    token = request.cookies.get(settings.cookie_name)

    # Fallback para header Authorization
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "MISSING_TOKEN",
                "message": "Token de autenticação não fornecido"
            }
        )

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
