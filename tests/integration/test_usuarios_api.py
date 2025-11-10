"""
Testes de integração para API de usuários
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_create_usuario():
    """Testa criação de usuário via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/usuarios", json={
            "nome": "João Silva",
            "email": "joao@example.com"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "USUARIO_CREATED"
        assert data["message"] == "Usuário criado com sucesso"
        assert data["data"]["nome"] == "João Silva"
        assert data["data"]["email"] == "joao@example.com"
        assert "id" in data["data"]
        assert "criado_em" in data["data"]


@pytest.mark.asyncio
async def test_create_usuario_sem_email():
    """Testa criação de usuário sem email"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/usuarios", json={
            "nome": "Maria Santos"
            # Sem email - deve ser permitido
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "USUARIO_CREATED"
        assert data["data"]["nome"] == "Maria Santos"
        assert data["data"]["email"] is None


@pytest.mark.asyncio
async def test_list_usuarios():
    """Testa listagem de usuários"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar alguns usuários primeiro
        await client.post("/api/v1/usuarios", json={
            "nome": "Usuário 1",
            "email": "user1@example.com"
        })
        await client.post("/api/v1/usuarios", json={
            "nome": "Usuário 2",
            "email": "user2@example.com"
        })

        # Listar
        response = await client.get("/api/v1/usuarios")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_usuario():
    """Testa busca de usuário por ID"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/usuarios", json={
            "nome": "Usuário Teste",
            "email": "teste@example.com"
        })
        assert create_response.status_code == 201, f"Erro ao criar usuário: {create_response.text}"
        create_data = create_response.json()
        assert create_data is not None, "Resposta não contém JSON válido"
        assert "data" in create_data, f"Resposta não contém 'data': {create_data}"
        created_id = create_data["data"]["id"]

        # Buscar
        response = await client.get(f"/api/v1/usuarios/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_DETAIL_SUCCESS"
        assert data["data"]["id"] == created_id
        assert data["data"]["nome"] == "Usuário Teste"
        assert data["data"]["email"] == "teste@example.com"


@pytest.mark.asyncio
async def test_get_usuario_not_found():
    """Testa busca de usuário inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/usuarios/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Usuário não encontrado"


@pytest.mark.asyncio
async def test_update_usuario():
    """Testa atualização de usuário"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/usuarios", json={
            "nome": "Nome Original",
            "email": "original@example.com"
        })
        assert create_response.status_code == 201, f"Erro ao criar usuário: {create_response.text}"
        create_data = create_response.json()
        assert create_data is not None, "Resposta não contém JSON válido"
        assert "data" in create_data, f"Resposta não contém 'data': {create_data}"
        created_id = create_data["data"]["id"]

        # Atualizar
        response = await client.put(f"/api/v1/usuarios/{created_id}", json={
            "nome": "Nome Atualizado",
            "email": "atualizado@example.com"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_UPDATED"
        assert data["data"]["nome"] == "Nome Atualizado"
        assert data["data"]["email"] == "atualizado@example.com"


@pytest.mark.asyncio
async def test_delete_usuario():
    """Testa remoção de usuário"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/usuarios", json={
            "nome": "Usuário Para Deletar",
            "email": "deletar@example.com"
        })
        assert create_response.status_code == 201, f"Erro ao criar usuário: {create_response.text}"
        create_data = create_response.json()
        assert create_data is not None, "Resposta não contém JSON válido"
        assert "data" in create_data, f"Resposta não contém 'data': {create_data}"
        created_id = create_data["data"]["id"]

        # Deletar
        response = await client.delete(f"/api/v1/usuarios/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_DELETED"

        # Verificar que foi deletado
        get_response = await client.get(f"/api/v1/usuarios/{created_id}")
        assert get_response.status_code == 404
        error_data = get_response.json()
        assert error_data["detail"] == "Usuário não encontrado"


@pytest.mark.asyncio
async def test_create_usuario_invalid_data():
    """Testa criação com dados inválidos"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Nome vazio
        response = await client.post("/api/v1/usuarios", json={
            "nome": "",  # Nome vazio (inválido)
            "email": "teste@example.com"
        })

        assert response.status_code == 422  # Validation error do Pydantic

        # Email inválido
        response = await client.post("/api/v1/usuarios", json={
            "nome": "Nome Válido",
            "email": "email-invalido"  # Email sem @
        })

        assert response.status_code == 422  # Validation error do Pydantic


@pytest.mark.asyncio
async def test_list_usuarios_with_filters():
    """Testa listagem de usuários com filtros"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar usuários com nomes específicos
        await client.post("/api/v1/usuarios", json={
            "nome": "João Silva",
            "email": "joao@example.com"
        })
        await client.post("/api/v1/usuarios", json={
            "nome": "Maria Santos",
            "email": "maria@example.com"
        })

        # Listar com filtro por nome
        response = await client.get("/api/v1/usuarios?nome=João")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        # Verificar que todos os usuários contêm "João" no nome
        for usuario in data["data"]:
            assert "João" in usuario["nome"]


@pytest.mark.asyncio
async def test_get_usuario_by_email():
    """Testa busca de usuário por email"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar usuário
        await client.post("/api/v1/usuarios", json={
            "nome": "Usuário Email Teste",
            "email": "emailteste@example.com"
        })

        # Buscar por email
        response = await client.get("/api/v1/usuarios/email/emailteste@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "USUARIO_DETAIL_SUCCESS"
        assert data["data"]["email"] == "emailteste@example.com"
        assert data["data"]["nome"] == "Usuário Email Teste"


@pytest.mark.asyncio
async def test_get_usuario_by_email_not_found():
    """Testa busca de usuário por email inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/usuarios/email/naoexiste@example.com")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Usuário não encontrado"
