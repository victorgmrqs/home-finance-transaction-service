"""
Testes de integração para API de categorias
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_list_categorias():
    """Testa listagem de categorias via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/categorias")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "Categorias listadas com sucesso"
        assert isinstance(data["data"], list)

        # Em ambiente de teste, pode não haver categorias padrão
        # Vamos apenas verificar se a estrutura está correta
        if len(data["data"]) > 0:
            categoria = data["data"][0]
            assert "id" in categoria
            assert "nome" in categoria
            assert "is_default" in categoria
            assert "usuario_id" in categoria
            assert "criado_em" in categoria
            assert "atualizado_em" in categoria


@pytest.mark.asyncio
async def test_create_categoria():
    """Testa criação de categoria customizada via API"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/categorias", json={
            "nome": "Academia",
            "descricao": "Gastos com academia e personal trainer"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "CREATED"
        assert data["message"] == "Categoria criada com sucesso"
        assert data["data"]["nome"] == "Academia"
        assert data["data"]["descricao"] == "Gastos com academia e personal trainer"
        assert data["data"]["is_default"] is False
        assert data["data"]["usuario_id"] == 1  # Mock user ID
        assert "id" in data["data"]
        assert "criado_em" in data["data"]


@pytest.mark.asyncio
async def test_create_categoria_sem_descricao():
    """Testa criação de categoria sem descrição"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/categorias", json={
            "nome": "Pets"
            # Sem descrição - deve ser permitido
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "CREATED"
        assert data["data"]["nome"] == "Pets"
        assert data["data"]["descricao"] is None


@pytest.mark.asyncio
async def test_create_categoria_nome_vazio():
    """Testa erro ao criar categoria com nome vazio"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/categorias", json={
            "nome": "",
            "descricao": "Nome vazio"
        })

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_categoria_nome_muito_longo():
    """Testa erro ao criar categoria com nome muito longo"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/categorias", json={
            "nome": "A" * 101,  # Mais de 100 caracteres
            "descricao": "Nome muito longo"
        })

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_categoria():
    """Testa busca de categoria por ID"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro criar uma categoria
        create_response = await client.post("/api/v1/categorias", json={
            "nome": "Teste Get",
            "descricao": "Categoria para teste de busca"
        })
        categoria_id = create_response.json()["data"]["id"]

        # Buscar a categoria criada
        response = await client.get(f"/api/v1/categorias/{categoria_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "Categoria encontrada"
        assert data["data"]["id"] == categoria_id
        assert data["data"]["nome"] == "Teste Get"


@pytest.mark.asyncio
async def test_get_categoria_not_found():
    """Testa busca de categoria inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/categorias/99999")

        assert response.status_code == 404
        data = response.json()
        assert "não encontrada" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_categoria():
    """Testa atualização de categoria customizada"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro criar uma categoria
        create_response = await client.post("/api/v1/categorias", json={
            "nome": "Original",
            "descricao": "Descrição original"
        })
        categoria_id = create_response.json()["data"]["id"]

        # Atualizar a categoria
        response = await client.put(f"/api/v1/categorias/{categoria_id}", json={
            "nome": "Atualizada",
            "descricao": "Descrição atualizada"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "Categoria atualizada com sucesso"
        assert data["data"]["nome"] == "Atualizada"
        assert data["data"]["descricao"] == "Descrição atualizada"


@pytest.mark.asyncio
async def test_update_categoria_partial():
    """Testa atualização parcial de categoria"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro criar uma categoria
        create_response = await client.post("/api/v1/categorias", json={
            "nome": "Original",
            "descricao": "Descrição original"
        })
        categoria_id = create_response.json()["data"]["id"]

        # Atualizar apenas o nome
        response = await client.put(f"/api/v1/categorias/{categoria_id}", json={
            "nome": "Só Nome Atualizado"
            # Sem descrição - deve manter a original
        })

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["nome"] == "Só Nome Atualizado"
        assert data["data"]["descricao"] == "Descrição original"


@pytest.mark.asyncio
async def test_update_categoria_not_found():
    """Testa atualização de categoria inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.put("/api/v1/categorias/99999", json={
            "nome": "Atualizada"
        })

        assert response.status_code == 404
        data = response.json()
        assert "não encontrada" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_categoria():
    """Testa exclusão de categoria customizada"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Primeiro criar uma categoria
        create_response = await client.post("/api/v1/categorias", json={
            "nome": "Para Deletar",
            "descricao": "Categoria que será deletada"
        })
        categoria_id = create_response.json()["data"]["id"]

        # Deletar a categoria
        response = await client.delete(f"/api/v1/categorias/{categoria_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert data["message"] == "Categoria deletada com sucesso"
        assert data["data"] is None

        # Verificar se foi realmente deletada
        get_response = await client.get(f"/api/v1/categorias/{categoria_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_categoria_not_found():
    """Testa exclusão de categoria inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.delete("/api/v1/categorias/99999")

        assert response.status_code == 404
        data = response.json()
        assert "não encontrada" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_categoria_duplicate_name():
    """Testa erro ao criar categoria com nome duplicado"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar primeira categoria
        await client.post("/api/v1/categorias", json={
            "nome": "Duplicada",
            "descricao": "Primeira categoria"
        })

        # Tentar criar segunda categoria com mesmo nome
        response = await client.post("/api/v1/categorias", json={
            "nome": "Duplicada",
            "descricao": "Segunda categoria"
        })

        assert response.status_code == 409
        data = response.json()
        assert "já existe" in data["detail"].lower()


@pytest.mark.asyncio
async def test_update_categoria_duplicate_name():
    """Testa erro ao atualizar categoria com nome duplicado"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar duas categorias
        await client.post("/api/v1/categorias", json={
            "nome": "Categoria 1",
            "descricao": "Primeira categoria"
        })

        cat2_response = await client.post("/api/v1/categorias", json={
            "nome": "Categoria 2",
            "descricao": "Segunda categoria"
        })
        cat2_id = cat2_response.json()["data"]["id"]

        # Tentar atualizar segunda categoria com nome da primeira
        response = await client.put(f"/api/v1/categorias/{cat2_id}", json={
            "nome": "Categoria 1"
        })

        assert response.status_code == 409
        data = response.json()
        assert "já existe" in data["detail"].lower()
