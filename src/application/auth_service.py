"""
Serviço de aplicação: Autenticação
Responsável pela lógica de login, registro e geração de tokens
"""


from datetime import UTC

from src.core.security import JWTManager, PasswordHasher, PasswordValidator
from src.domain.exceptions import (
    BusinessRuleViolationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from src.domain.models.usuario import Usuario
from src.ports.usuario_port import UsuarioRepositoryPort


class AuthService:
    """Serviço de autenticação de usuários"""

    def __init__(self, usuario_repository: UsuarioRepositoryPort):
        """
        Inicializa o serviço de autenticação

        Args:
            usuario_repository: Repositório de usuários
        """
        self.usuario_repository = usuario_repository
        self.password_hasher = PasswordHasher()
        self.password_validator = PasswordValidator()
        self.jwt_manager = JWTManager()

    async def register(
        self,
        nome: str,
        email: str,
        password: str
    ) -> tuple[Usuario, str]:
        """
        Registra um novo usuário no sistema

        Args:
            nome: Nome do usuário
            email: Email do usuário
            password: Senha em texto plano

        Returns:
            Tupla (usuario, token_jwt)

        Raises:
            BusinessRuleViolationError: Se a senha não atender aos requisitos
            DuplicateEntityError: Se o email já estiver cadastrado
        """
        # Valida força da senha
        is_valid, error_message = self.password_validator.validate(password)
        if not is_valid:
            raise BusinessRuleViolationError(error_message)

        # Verifica se email já existe
        existing_user = await self.usuario_repository.get_by_email(email)
        if existing_user:
            raise DuplicateEntityError("Email já cadastrado")

        # Hash da senha
        password_hash = self.password_hasher.hash_password(password)

        # Cria o usuário
        usuario = Usuario(
            id=None,
            nome=nome,
            email=email,
            password_hash=password_hash
        )

        # Persiste no banco
        usuario_criado = await self.usuario_repository.create(usuario)

        # Gera token JWT
        token = self.jwt_manager.create_access_token(
            data={
                "sub": str(usuario_criado.id),
                "email": usuario_criado.email,
                "nome": usuario_criado.nome
            }
        )

        return usuario_criado, token

    async def login(
        self,
        email: str,
        password: str
    ) -> tuple[Usuario, str]:
        """
        Autentica um usuário

        Args:
            email: Email do usuário
            password: Senha em texto plano

        Returns:
            Tupla (usuario, token_jwt)

        Raises:
            BusinessRuleViolationError: Se credenciais inválidas
        """
        # Busca usuário por email
        usuario = await self.usuario_repository.get_by_email(email)
        if not usuario:
            raise BusinessRuleViolationError("Credenciais inválidas")

        # Verifica se usuário tem senha cadastrada
        if not usuario.password_hash:
            raise BusinessRuleViolationError(
                "Usuário não possui senha cadastrada. Use a recuperação de senha."
            )

        # Verifica senha
        if not self.password_hasher.verify_password(password, usuario.password_hash):
            raise BusinessRuleViolationError("Credenciais inválidas")

        # Gera token JWT
        token = self.jwt_manager.create_access_token(
            data={
                "sub": str(usuario.id),
                "email": usuario.email,
                "nome": usuario.nome
            }
        )

        return usuario, token

    async def verify_token(self, token: str) -> dict | None:
        """
        Verifica e decodifica um token JWT

        Args:
            token: Token JWT

        Returns:
            Payload do token ou None se inválido
        """
        payload = self.jwt_manager.decode_access_token(token)
        if not payload:
            return None

        # Validação manual de expiração (já que desabilitamos verify_exp no decode)
        from datetime import datetime
        exp_timestamp = payload.get("exp")
        if exp_timestamp and isinstance(exp_timestamp, (int, float)):
            exp_datetime = datetime.fromtimestamp(float(exp_timestamp), tz=UTC)
            if exp_datetime < datetime.now(UTC):
                # Token expirado
                return None

        return payload

    async def get_current_user(self, token: str) -> Usuario | None:
        """
        Obtém o usuário atual a partir do token

        Args:
            token: Token JWT

        Returns:
            Usuario ou None se token inválido
        """
        payload = self.jwt_manager.decode_access_token(token)
        if not payload:
            return None

        # Validação manual de expiração (já que desabilitamos verify_exp no decode)
        from datetime import datetime
        exp_timestamp = payload.get("exp")
        if exp_timestamp and isinstance(exp_timestamp, (int, float)):
            exp_datetime = datetime.fromtimestamp(float(exp_timestamp), tz=UTC)
            if exp_datetime < datetime.now(UTC):
                # Token expirado
                return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user_id_int = int(str(user_id))
            return await self.usuario_repository.get_by_id(user_id_int)
        except (EntityNotFoundError, ValueError, TypeError):
            return None

    async def get_session_info(self, token: str) -> dict | None:
        """
        Obtém informações completas da sessão do usuário

        Args:
            token: Token JWT

        Returns:
            Dict com user e session info, ou None se token inválido

        Validações:
        - Token válido e não expirado
        - Usuário ainda existe no banco (validação de integridade)
        - Dados do token correspondem aos dados do banco
        """
        # Decodifica e valida token
        payload = self.jwt_manager.decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Busca usuário no banco (validação de integridade)
        try:
            user_id_int = int(str(user_id))
            usuario = await self.usuario_repository.get_by_id(user_id_int)
        except (EntityNotFoundError, ValueError, TypeError):
            return None

        if not usuario:
            return None

        # Valida correspondência de dados entre token e banco
        token_email = payload.get("email")
        if token_email and token_email != usuario.email:
            # Token desatualizado - usuário mudou email
            return None

        # Extrai informações de tempo do token
        from datetime import datetime
        exp_timestamp = payload.get("exp")
        iat_timestamp = payload.get("iat")

        # Validação manual de expiração (já que desabilitamos verify_exp no decode)
        if exp_timestamp and isinstance(exp_timestamp, (int, float)):
            exp_datetime = datetime.fromtimestamp(float(exp_timestamp), tz=UTC)
            if exp_datetime < datetime.now(UTC):
                # Token expirado
                return None

        expires_at = None
        issued_at = None

        if exp_timestamp and isinstance(exp_timestamp, (int, float)):
            expires_at = datetime.fromtimestamp(float(exp_timestamp), tz=UTC).isoformat()
        if iat_timestamp and isinstance(iat_timestamp, (int, float)):
            issued_at = datetime.fromtimestamp(float(iat_timestamp), tz=UTC).isoformat()

        # Retorna informações completas
        return {
            "user": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "criado_em": usuario.criado_em.isoformat() if usuario.criado_em else None
            },
            "session": {
                "valid": True,
                "expires_at": expires_at,
                "issued_at": issued_at
            }
        }
