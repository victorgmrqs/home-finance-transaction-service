"""
Módulo de segurança - Hash de senhas e JWT
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from src.core.config import settings


class PasswordHasher:
    """Gerenciador de hash de senhas usando bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash de uma senha usando bcrypt

        Args:
            password: Senha em texto plano

        Returns:
            Hash da senha em formato string
        """
        # Gera salt e hash
        salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash

        Args:
            password: Senha em texto plano
            password_hash: Hash da senha armazenado

        Returns:
            True se a senha corresponde ao hash, False caso contrário
        """
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except (ValueError, TypeError):
            return False


class PasswordValidator:
    """Validador de força de senha"""

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = False

    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """
        Valida força de senha

        Args:
            password: Senha a ser validada

        Returns:
            Tupla (is_valid, error_message)
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Senha deve ter pelo menos {cls.MIN_LENGTH} caracteres"

        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Senha deve conter pelo menos uma letra maiúscula"

        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Senha deve conter pelo menos uma letra minúscula"

        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Senha deve conter pelo menos um dígito"

        if cls.REQUIRE_SPECIAL:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if all(c not in special_chars for c in password):
                return False, "Senha deve conter pelo menos um caractere especial"

        return True, ""


class JWTManager:
    """Gerenciador de tokens JWT"""

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
    ) -> str:
        """
        Cria um token JWT de acesso

        Args:
            data: Dados a serem codificados no token
            expires_delta: Tempo de expiração customizado (opcional)

        Returns:
            Token JWT codificado
        """
        now = datetime.now(UTC)

        # Define expiração
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        # Converte datetime para UNIX timestamp
        to_encode = data.copy() | {
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp())
        }

        # Codifica o token
        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm="HS256"
        )

    @staticmethod
    def decode_access_token(token: str) -> dict[str, object] | None:
        """
        Decodifica e valida um token JWT

        Args:
            token: Token JWT a ser decodificado

        Returns:
            Dados decodificados do token ou None se inválido
        """
        try:
            decoded = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            return dict(decoded)
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
