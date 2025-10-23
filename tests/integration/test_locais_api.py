"""
Testes de integracao para API de locais
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_create_local():
    """Testa criacao de local via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Supermercado Exemplo",
            "cnpj": "12345678000190",
            "razao_social": "Supermercado Exemplo LTDA",
            "categoria": "supermercado"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "LOCAL_CREATED"
        assert data["data"]["nome_fantasia"] == "Supermercado Exemplo"


@pytest.mark.asyncio
async def test_create_local_minimal():
    """Testa criacao de local com dados minimos (ADR-002)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Padaria do Joao"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "LOCAL_CREATED"


@pytest.mark.asyncio
async def test_list_locais():
    """Testa listagem de locais"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar local primeiro
        await client.post("/api/v1/locais", json={
            "nome_fantasia": "Farmacia Central"
        })

        # Listar
        response = await client.get("/api/v1/locais")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "LOCAL_LIST_SUCCESS"
        assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_local():
    """Testa busca de local por ID"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Loja de Teste"
        })
        created_id = create_response.json()["data"]["id"]

        # Buscar
        response = await client.get(f"/api/v1/locais/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "LOCAL_DETAIL_SUCCESS"
        assert data["data"]["id"] == created_id


@pytest.mark.asyncio
async def test_update_local():
    """Testa atualizacao de local (completar dados - ADR-002)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar local incompleto
        create_response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Loja Incompleta"
        })
        created_id = create_response.json()["data"]["id"]

        # Completar dados
        response = await client.put(f"/api/v1/locais/{created_id}", json={
            "cnpj": "98765432000199",
            "razao_social": "Loja Completa LTDA"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "LOCAL_UPDATED"
        assert data["data"]["cnpj"] == "98765432000199"


@pytest.mark.asyncio
async def test_delete_local():
    """Testa remocao de local"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Para deletar"
        })
        created_id = create_response.json()["data"]["id"]

        # Deletar
        response = await client.delete(f"/api/v1/locais/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "LOCAL_DELETED"


@pytest.mark.asyncio
async def test_create_local_duplicate_cnpj():
    """Testa criacao com CNPJ duplicado"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        cnpj = "11222333000144"

        # Criar primeiro
        await client.post("/api/v1/locais", json={
            "nome_fantasia": "Primeiro",
            "cnpj": cnpj
        })

        # Tentar criar com mesmo CNPJ
        response = await client.post("/api/v1/locais", json={
            "nome_fantasia": "Segundo",
            "cnpj": cnpj
        })

        assert response.status_code == 409
        data = response.json()
        assert data["code"] == "DUPLICATE_CNPJ"
