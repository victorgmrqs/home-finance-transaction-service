"""
Serviço de aplicação: Autenticação
Responsável pela lógica de login, registro e geração de tokens
"""


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
        return self.jwt_manager.decode_access_token(token)

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

        user_id = payload.get("sub")
        if not user_id:
            return None

        try:
            user_id_int = int(str(user_id))
            return await self.usuario_repository.get_by_id(user_id_int)
        except (EntityNotFoundError, ValueError, TypeError):
            return None
