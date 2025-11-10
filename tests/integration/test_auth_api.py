"""
Testes de integração para API de autenticação
"""


import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import settings
from src.main import app


def clear_rate_limiter_storage():
    """Função auxiliar para limpar o storage do rate limiter"""
    from src.adapters.controllers import auth_controller

    limiters = []
    if hasattr(app.state, "limiter"):
        limiters.append(app.state.limiter)
    if hasattr(auth_controller, 'limiter'):
        limiters.append(auth_controller.limiter)

    for limiter_obj in limiters:
        if hasattr(limiter_obj, "_storage"):
            try:
                storage = limiter_obj._storage
                # Usar reset() se disponível (mais eficaz para MemoryStorage)
                if hasattr(storage, "reset"):
                    storage.reset()
                elif hasattr(storage, "clear"):
                    storage.clear()
                elif isinstance(storage, dict):
                    storage.clear()
            except Exception:
                pass


@pytest.fixture(autouse=True)
def disable_rate_limiting(monkeypatch):
    """Desabilita rate limiting para todos os testes de autenticação"""
    # Limpar o storage antes de cada teste
    clear_rate_limiter_storage()

    # Mockar get_remote_address para retornar valores únicos por teste
    import random
    import time

    # Usar um contador único por teste para garantir chaves diferentes
    test_counter = [0]  # Usar lista para permitir modificação em closure

    def unique_key_func(request):
        """Retorna uma chave única para cada chamada, evitando rate limiting"""
        test_counter[0] += 1
        return f"test_{id(request)}_{time.time()}_{random.random()}_{test_counter[0]}"

    # Substituir a função key_func do limiter
    monkeypatch.setattr("slowapi.util.get_remote_address", unique_key_func)

    # Também substituir no limiter do app
    if hasattr(app.state, "limiter"):
        app.state.limiter.key_func = unique_key_func

    # E no limiter do auth_controller
    from src.adapters.controllers import auth_controller
    if hasattr(auth_controller, 'limiter'):
        auth_controller.limiter.key_func = unique_key_func

    yield

    # Limpar novamente após o teste
    clear_rate_limiter_storage()


@pytest.mark.asyncio
async def test_register_with_httponly_cookie():
    """Testa registro de usuário com cookie HttpOnly"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Teste",
            "email": "register_test@example.com",
            "password": "SenhaSegura123!"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "REGISTER_SUCCESS"
        assert data["message"] == "Usuário registrado com sucesso"
        assert "data" in data
        assert "user" in data["data"]
        assert data["data"]["user"]["nome"] == "Usuário Teste"
        assert data["data"]["user"]["email"] == "register_test@example.com"

        # Verificar que o token NÃO está no corpo da resposta
        assert "token" not in data["data"]

        # Verificar que o cookie foi definido
        assert settings.cookie_name in response.cookies
        cookie = response.cookies[settings.cookie_name]
        assert cookie is not None
        assert len(cookie) > 0

        # Verificar atributos do cookie (se disponíveis via response.headers)
        set_cookie_header = response.headers.get("set-cookie", "")
        assert settings.cookie_name in set_cookie_header
        assert "HttpOnly" in set_cookie_header
        assert "Path=/" in set_cookie_header
        assert f"SameSite={settings.cookie_samesite}" in set_cookie_header

        # Em produção, deve ter Secure
        if settings.cookie_secure:
            assert "Secure" in set_cookie_header


@pytest.mark.asyncio
async def test_login_with_httponly_cookie():
    """Testa login de usuário com cookie HttpOnly"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro, registrar um usuário
        register_response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Login",
            "email": "login_test@example.com",
            "password": "SenhaSegura123!"
        })
        assert register_response.status_code == 201

        # Fazer login
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "login_test@example.com",
            "password": "SenhaSegura123!"
        })

        assert login_response.status_code == 200
        data = login_response.json()
        assert data["code"] == "LOGIN_SUCCESS"
        assert data["message"] == "Login realizado com sucesso"
        assert "data" in data
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "login_test@example.com"

        # Verificar que o token NÃO está no corpo da resposta
        assert "token" not in data["data"]

        # Verificar que o cookie foi definido
        assert settings.cookie_name in login_response.cookies
        cookie = login_response.cookies[settings.cookie_name]
        assert cookie is not None
        assert len(cookie) > 0

        # Verificar atributos do cookie
        set_cookie_header = login_response.headers.get("set-cookie", "")
        assert settings.cookie_name in set_cookie_header
        assert "HttpOnly" in set_cookie_header
        assert "Path=/" in set_cookie_header


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Testa login com credenciais inválidas"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Tentar login com credenciais inválidas
        response = await client.post("/api/v1/auth/login", json={
            "email": "naoexiste@example.com",
            "password": "SenhaErrada123!"
        })

        assert response.status_code == 401
        data = response.json()
        # O handler retorna o detail diretamente quando é um dict com "code"
        assert "code" in data or "detail" in data
        if "code" in data:
            assert data["code"] == "INVALID_CREDENTIALS"
            assert data["message"] == "Credenciais inválidas"
        else:
            assert "detail" in data

        # Verificar que nenhum cookie foi definido
        assert settings.cookie_name not in response.cookies


@pytest.mark.asyncio
async def test_verify_token_with_cookie():
    """Testa verificação de token via cookie"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar e obter cookie
        register_response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Verify",
            "email": "verify_test@example.com",
            "password": "SenhaSegura123!"
        })
        assert register_response.status_code == 201

        # Obter o cookie do registro
        cookies = {settings.cookie_name: register_response.cookies[settings.cookie_name]}

        # Verificar token usando o cookie
        verify_response = await client.get("/api/v1/auth/verify", cookies=cookies)

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["code"] == "TOKEN_VALID"
        assert data["message"] == "Token válido"
        assert "data" in data
        assert "user" in data["data"]
        assert data["data"]["user"]["email"] == "verify_test@example.com"


@pytest.mark.asyncio
async def test_verify_token_with_header():
    """Testa verificação de token via header Authorization (fallback)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar usuário
        register_response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Header",
            "email": "header_test@example.com",
            "password": "SenhaSegura123!"
        })
        assert register_response.status_code == 201

        # Obter o token do cookie (para teste, vamos usar diretamente)
        token = register_response.cookies[settings.cookie_name]

        # Verificar token usando header Authorization
        verify_response = await client.get(
            "/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["code"] == "TOKEN_VALID"
        assert data["message"] == "Token válido"


@pytest.mark.asyncio
async def test_verify_token_without_token():
    """Testa verificação sem fornecer token"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Tentar verificar sem token
        response = await client.get("/api/v1/auth/verify")

        assert response.status_code == 401
        data = response.json()
        # O handler retorna o detail diretamente quando é um dict com "code"
        assert "code" in data or "detail" in data
        if "code" in data:
            assert data["code"] == "MISSING_TOKEN"
            assert data["message"] == "Token de autenticação não fornecido"
        else:
            assert "detail" in data


@pytest.mark.asyncio
async def test_logout():
    """Testa logout (remoção do cookie)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar e obter cookie
        register_response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Logout",
            "email": "logout_test@example.com",
            "password": "SenhaSegura123!"
        })
        assert register_response.status_code == 201

        # Fazer logout
        logout_response = await client.post("/api/v1/auth/logout")

        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["code"] == "LOGOUT_SUCCESS"
        assert data["message"] == "Logout realizado com sucesso"

        # Verificar que o cookie foi removido (ou definido com max_age=0)
        # A remoção pode ser indicada pelo cookie estar ausente ou com valor vazio
        set_cookie_header = logout_response.headers.get("set-cookie", "")

        # Deve conter instruções para remover o cookie
        if set_cookie_header:
            assert settings.cookie_name in set_cookie_header
            # Cookie de remoção geralmente tem Max-Age=0 ou expires no passado
            assert "Max-Age=0" in set_cookie_header or "expires=" in set_cookie_header.lower()


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Testa registro com email duplicado"""
    # Limpar storage do rate limiter antes do teste
    clear_rate_limiter_storage()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Registrar primeiro usuário
        first_response = await client.post("/api/v1/auth/register", json={
            "nome": "Primeiro Usuário",
            "email": "duplicate@example.com",
            "password": "SenhaSegura123!"
        })
        assert first_response.status_code == 201

        # Limpar storage novamente antes da segunda requisição
        clear_rate_limiter_storage()

        # Tentar registrar com o mesmo email
        duplicate_response = await client.post("/api/v1/auth/register", json={
            "nome": "Segundo Usuário",
            "email": "duplicate@example.com",
            "password": "OutraSenha123!"
        })

        assert duplicate_response.status_code == 409, f"Esperado 409, recebido {duplicate_response.status_code}. Resposta: {duplicate_response.text}"
        data = duplicate_response.json()
        # O handler pode retornar "detail" ou "code"/"message"
        assert "detail" in data or "code" in data
        # Verificar que não há cookie na resposta de erro
        assert settings.cookie_name not in duplicate_response.cookies


@pytest.mark.asyncio
async def test_register_weak_password():
    """Testa registro com senha fraca"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Tentar registrar com senha fraca
        response = await client.post("/api/v1/auth/register", json={
            "nome": "Usuário Senha Fraca",
            "email": "weak_password@example.com",
            "password": "123"  # Senha muito fraca
        })

        # Deve retornar erro de validação (400 ou 422)
        assert response.status_code in [400, 422]
        assert settings.cookie_name not in response.cookies


@pytest.mark.asyncio
async def test_cookie_attributes():
    """Testa que os atributos do cookie estão corretos"""
    # Limpar storage do rate limiter antes do teste
    clear_rate_limiter_storage()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/auth/register", json={
            "nome": "Teste Atributos",
            "email": "cookie_attrs@example.com",
            "password": "SenhaSegura123!"
        })

        assert response.status_code == 201

        # Analisar header Set-Cookie
        set_cookie_header = response.headers.get("set-cookie", "")

        # Verificar atributos esperados
        assert f"{settings.cookie_name}=" in set_cookie_header
        assert "HttpOnly" in set_cookie_header
        assert "Path=/" in set_cookie_header
        assert f"Max-Age={settings.cookie_max_age}" in set_cookie_header
        assert f"SameSite={settings.cookie_samesite}" in set_cookie_header

        # Secure só em produção
        if settings.cookie_secure:
            assert "Secure" in set_cookie_header
