"""
Middleware de Autenticação Mock
Simula autenticação para desenvolvimento e testes
Em produção, deve ser substituído por autenticação real (JWT, OAuth2, etc.)
"""

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class MockAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticação mock para desenvolvimento

    Em desenvolvimento, usa o header X-User-ID para simular autenticação.
    Se não fornecido, usa usuario_id=1 como padrão.

    Em produção, este middleware deve ser substituído por autenticação real.
    """

    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment

        # Rotas públicas que não precisam de autenticação
        self.public_routes = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",      # Healthcheck (novo padrão)
            "/api/v1/health",  # Backward compatibility (deprecar no futuro)
            "/info"
        ]

    async def dispatch(self, request: Request, call_next):
        """Processa a requisição e injeta o usuario_id"""

        # Permitir rotas públicas sem autenticação
        if request.url.path in self.public_routes:
            return await call_next(request)

        # Em desenvolvimento, usar mock de autenticação
        if self.environment == "development":
            user_id = self._get_mock_user_id(request)
            request.state.usuario_id = user_id
            request.state.authenticated = True
        else:
            # Em produção, isso deveria validar um token real
            # Por enquanto, retorna erro
            raise HTTPException(
                status_code=501,
                detail="Autenticação real não implementada. Configure um sistema de autenticação."
            )

        response = await call_next(request)
        return response

    def _get_mock_user_id(self, request: Request) -> int:
        """
        Obtém o ID do usuário do header X-User-ID ou usa padrão

        Em desenvolvimento:
        - Se header X-User-ID está presente, usa esse valor
        - Caso contrário, usa usuario_id = 1 como padrão
        """
        user_id_header = request.headers.get("X-User-ID")

        if user_id_header:
            try:
                return int(user_id_header)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Header X-User-ID inválido: {user_id_header}"
                )

        # Padrão: usuário 1
        return 1


def get_current_user_id(request: Request) -> int:
    """
    Dependency para obter o usuario_id autenticado

    Usage:
        @router.get("/endpoint")
        async def endpoint(usuario_id: int = Depends(get_current_user_id)):
            ...
    """
    if not hasattr(request.state, "usuario_id"):
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado"
        )

    usuario_id = getattr(request.state, "usuario_id", None)
    if usuario_id is None or not isinstance(usuario_id, int):
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado"
        )
    return int(usuario_id)


def check_painel_permission(
    request: Request,
    painel_id: int,
    required_permission: str = "VIEWER"
) -> bool:
    """
    Verifica se o usuário tem permissão para acessar o painel

    Args:
        request: Request object com usuario_id no state
        painel_id: ID do painel
        required_permission: OWNER, EDITOR ou VIEWER

    Returns:
        bool: True se tem permissão, False caso contrário

    Note:
        Esta é uma versão simplificada. Em produção, deveria consultar
        a tabela painel_usuarios para verificar permissões reais.
    """
    # Versão mock: sempre retorna True
    # Em produção, consultar tabela painel_usuarios
    return True
