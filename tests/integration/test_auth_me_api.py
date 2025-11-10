"""
Testes de integração para endpoint GET /auth/me
"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_auth_me_with_valid_cookie():
    """Testa GET /auth/me com cookie válido"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro, fazer login para obter cookie
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "nome": "Session User",
                "email": "session@example.com",
                "password": "SecurePass123"
            }
        )

        assert register_response.status_code == 201

        # Extrair cookie do Set-Cookie header
        cookies = register_response.cookies

        # Fazer requisição para /auth/me com o cookie
        me_response = await client.get(
            "/api/v1/auth/me",
            cookies=cookies
        )

        assert me_response.status_code == 200
        data = me_response.json()

        assert data["code"] == "SESSION_VALID"
        assert data["message"] == "Sessão recuperada com sucesso"
        assert "user" in data["data"]
        assert "session" in data["data"]

        # Validar dados do usuário
        user_data = data["data"]["user"]
        assert user_data["nome"] == "Session User"
        assert user_data["email"] == "session@example.com"
        assert "id" in user_data
        assert "criado_em" in user_data

        # Validar dados da sessão
        session_data = data["data"]["session"]
        assert session_data["valid"] is True
        assert "expires_at" in session_data
        assert "issued_at" in session_data


@pytest.mark.asyncio
async def test_auth_me_without_token():
    """Testa GET /auth/me sem token (cookie ou header)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()

        # O handler pode retornar "detail" ou "code"/"message" diretamente
        if "detail" in data:
            assert data["detail"]["code"] == "MISSING_TOKEN"
            assert "não fornecido" in data["detail"]["message"].lower()
        else:
            assert data["code"] == "MISSING_TOKEN"
            assert "não fornecido" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_me_with_invalid_cookie():
    """Testa GET /auth/me com cookie inválido"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/auth/me",
            cookies={"auth_token": "invalid_token_here"}
        )

        assert response.status_code == 401
        data = response.json()

        # O handler pode retornar "detail" ou "code"/"message" diretamente
        if "detail" in data:
            assert data["detail"]["code"] == "INVALID_SESSION"
        else:
            assert data["code"] == "INVALID_SESSION"


@pytest.mark.asyncio
async def test_auth_me_with_authorization_header():
    """Testa GET /auth/me com Authorization header (fallback)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar usuário
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "nome": "Header User",
                "email": "header@example.com",
                "password": "SecurePass123"
            }
        )

        assert register_response.status_code == 201

        # Extrair token (se ainda estiver no body - backward compatibility)
        # Ou fazer login novamente
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "header@example.com",
                "password": "SecurePass123"
            }
        )

        # Extrair token do cookie
        cookies = login_response.cookies
        token = cookies.get("auth_token")

        # Fazer requisição com Authorization header
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert me_response.status_code == 200
        data = me_response.json()

        assert data["code"] == "SESSION_VALID"
        assert data["data"]["user"]["email"] == "header@example.com"


@pytest.mark.asyncio
async def test_auth_me_response_structure():
    """Testa estrutura completa da resposta do /auth/me"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar e fazer login
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "nome": "Structure Test",
                "email": "structure@example.com",
                "password": "SecurePass123"
            }
        )

        cookies = register_response.cookies

        response = await client.get(
            "/api/v1/auth/me",
            cookies=cookies
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura base
        assert "code" in data
        assert "message" in data
        assert "data" in data

        # Verificar estrutura de dados
        assert "user" in data["data"]
        assert "session" in data["data"]

        # Verificar estrutura de user
        user = data["data"]["user"]
        assert "id" in user
        assert "nome" in user
        assert "email" in user
        assert "criado_em" in user

        # Verificar estrutura de session
        session = data["data"]["session"]
        assert "valid" in session
        assert "expires_at" in session
        assert "issued_at" in session

        # Validar tipos
        assert isinstance(user["id"], int)
        assert isinstance(user["nome"], str)
        assert isinstance(user["email"], str)
        assert isinstance(session["valid"], bool)
        assert isinstance(session["expires_at"], str)
        assert isinstance(session["issued_at"], str)


@pytest.mark.asyncio
async def test_auth_me_with_expired_token():
    """Testa GET /auth/me com token expirado"""
    import jwt
    from datetime import datetime, timedelta, UTC
    from src.core.config import settings

    # Gerar um token JWT expirado
    expired_payload = {
        "sub": "999",
        "email": "expired@example.com",
        "nome": "Expired User",
        "exp": int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),  # Expirado há 1 hora
        "iat": int((datetime.now(UTC) - timedelta(hours=2)).timestamp())
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.secret_key,
        algorithm="HS256"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        cookies = {settings.cookie_name: expired_token}
        response = await client.get("/api/v1/auth/me", cookies=cookies)
        
        assert response.status_code == 401
        data = response.json()
        
        # Verifica que a mensagem indica token inválido/expirado
        if "detail" in data:
            assert data["detail"]["code"] == "INVALID_SESSION"
            assert "inválida" in data["detail"]["message"].lower() or "expirada" in data["detail"]["message"].lower()
        else:
            assert data["code"] == "INVALID_SESSION"
            assert "inválida" in data["message"].lower() or "expirada" in data["message"].lower()
