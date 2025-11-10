"""
Testes unitários para recuperação de sessão no AuthService
"""
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.auth_service import AuthService
from src.domain.models.usuario import Usuario


@pytest.fixture
def mock_repository():
    """Mock do repository de usuários"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_repository):
    """Instância do AuthService com repository mock"""
    return AuthService(mock_repository)


@pytest.mark.asyncio
async def test_get_session_info_with_valid_token(auth_service, mock_repository):
    """Testa recuperação de sessão com token válido"""
    # Arrange
    usuario = Usuario(
        id=1,
        nome="Test User",
        email="test@example.com",
        password_hash="hash123",
        criado_em=datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    mock_repository.get_by_id.return_value = usuario

    # Create a valid token
    token_data = {
        "sub": "1",
        "email": "test@example.com",
        "nome": "Test User"
    }
    token = auth_service.jwt_manager.create_access_token(token_data)

    # Act
    result = await auth_service.get_session_info(token)

    # Assert
    assert result is not None
    assert result["user"]["id"] == 1
    assert result["user"]["nome"] == "Test User"
    assert result["user"]["email"] == "test@example.com"
    assert result["session"]["valid"] is True
    assert "expires_at" in result["session"]
    assert "issued_at" in result["session"]
    mock_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_session_info_with_invalid_token(auth_service):
    """Testa recuperação de sessão com token inválido"""
    # Act
    result = await auth_service.get_session_info("invalid_token")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_session_info_with_nonexistent_user(auth_service, mock_repository):
    """Testa recuperação de sessão quando usuário não existe mais"""
    # Arrange
    mock_repository.get_by_id.return_value = None

    token_data = {"sub": "999", "email": "deleted@example.com"}
    token = auth_service.jwt_manager.create_access_token(token_data)

    # Act
    result = await auth_service.get_session_info(token)

    # Assert
    assert result is None
    mock_repository.get_by_id.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_get_session_info_with_mismatched_email(auth_service, mock_repository):
    """Testa validação de integridade quando email mudou"""
    # Arrange
    usuario = Usuario(
        id=1,
        nome="Test User",
        email="newemail@example.com",  # Email mudou
        password_hash="hash123",
        criado_em=datetime.now(UTC)
    )
    mock_repository.get_by_id.return_value = usuario

    token_data = {
        "sub": "1",
        "email": "oldemail@example.com",  # Email antigo no token
        "nome": "Test User"
    }
    token = auth_service.jwt_manager.create_access_token(token_data)

    # Act
    result = await auth_service.get_session_info(token)

    # Assert
    assert result is None  # Token desatualizado, sessão inválida


@pytest.mark.asyncio
async def test_get_session_info_without_sub_in_token(auth_service):
    """Testa recuperação quando token não tem 'sub' (user_id)"""
    # Arrange - criar token manualmente sem 'sub'
    # Usar método privado para criar token sem validações
    import jwt as pyjwt

    from src.core.config import settings

    payload = {"email": "test@example.com"}  # Sem 'sub'
    token = pyjwt.encode(payload, settings.secret_key, algorithm="HS256")

    # Act
    result = await auth_service.get_session_info(token)

    # Assert
    assert result is None
