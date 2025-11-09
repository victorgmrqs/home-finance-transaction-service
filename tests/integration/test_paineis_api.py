"""
Testes de integração para API de painéis
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def setup_usuario():
    """Setup inicial: cria usuário para os testes"""
    async def _setup():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/usuarios", json={
                "nome": "Usuário Teste Painéis",
                "email": "testepaineis@example.com"
            })
            usuario_id = response.json()["data"]["id"]
            return usuario_id

    return _setup


@pytest.mark.asyncio
async def test_create_painel(setup_usuario):
    """Testa criação de painel via API"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/paineis", json={
            "nome": "Painel Casa",
            "descricao": "Gastos da casa",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "PAINEL_CREATED"
        assert data["message"] == "Painel criado com sucesso"
        assert data["data"]["nome"] == "Painel Casa"
        assert data["data"]["descricao"] == "Gastos da casa"
        assert data["data"]["usuario_id"] == usuario_id
        assert "id" in data["data"]
        assert "criado_em" in data["data"]


@pytest.mark.asyncio
async def test_create_painel_sem_descricao(setup_usuario):
    """Testa criação de painel sem descrição"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/paineis", json={
            "nome": "Painel Simples",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
            # Sem descrição - deve ser permitido
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "PAINEL_CREATED"
        assert data["data"]["nome"] == "Painel Simples"
        assert data["data"]["descricao"] is None
        assert data["data"]["usuario_id"] == usuario_id


@pytest.mark.asyncio
async def test_list_paineis(setup_usuario):
    """Testa listagem de painéis"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar alguns painéis primeiro
        await client.post("/api/v1/paineis", json={
            "nome": "Painel 1",
            "descricao": "Primeiro painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        await client.post("/api/v1/paineis", json={
            "nome": "Painel 2",
            "descricao": "Segundo painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        # Listar
        response = await client.get("/api/v1/paineis")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_painel(setup_usuario):
    """Testa busca de painel por ID"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/paineis", json={
            "nome": "Painel Teste",
            "descricao": "Painel para teste",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        created_id = create_response.json()["data"]["id"]

        # Buscar
        response = await client.get(f"/api/v1/paineis/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_DETAIL_SUCCESS"
        assert data["data"]["id"] == created_id
        assert data["data"]["nome"] == "Painel Teste"
        assert data["data"]["usuario_id"] == usuario_id


@pytest.mark.asyncio
async def test_get_painel_not_found():
    """Testa busca de painel inexistente"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/paineis/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "PAINEL_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_painel(setup_usuario):
    """Testa atualização de painel"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/paineis", json={
            "nome": "Nome Original",
            "descricao": "Descrição original",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        created_id = create_response.json()["data"]["id"]

        # Atualizar
        response = await client.put(f"/api/v1/paineis/{created_id}", json={
            "nome": "Nome Atualizado",
            "descricao": "Descrição atualizada"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_UPDATED"
        assert data["data"]["nome"] == "Nome Atualizado"
        assert data["data"]["descricao"] == "Descrição atualizada"


@pytest.mark.asyncio
async def test_delete_painel(setup_usuario):
    """Testa remoção de painel"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/paineis", json={
            "nome": "Painel Para Deletar",
            "descricao": "Será deletado",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        created_id = create_response.json()["data"]["id"]

        # Deletar
        response = await client.delete(f"/api/v1/paineis/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_DELETED"

        # Verificar que foi deletado
        get_response = await client.get(f"/api/v1/paineis/{created_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_painel_invalid_data(setup_usuario):
    """Testa criação com dados inválidos"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Nome vazio
        response = await client.post("/api/v1/paineis", json={
            "nome": "",  # Nome vazio (inválido)
            "descricao": "Descrição válida",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        assert response.status_code == 422  # Validation error do Pydantic

        # Usuario_id inválido
        response = await client.post("/api/v1/paineis", json={
            "nome": "Nome Válido",
            "descricao": "Descrição válida",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": 0  # ID inválido
        })

        assert response.status_code == 422  # Validation error do Pydantic


@pytest.mark.asyncio
async def test_list_paineis_by_usuario(setup_usuario):
    """Testa listagem de painéis por usuário"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar painéis para o usuário
        await client.post("/api/v1/paineis", json={
            "nome": "Painel Casa",
            "descricao": "Gastos da casa",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        await client.post("/api/v1/paineis", json={
            "nome": "Painel Trabalho",
            "descricao": "Gastos do trabalho",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        # Listar painéis do usuário
        response = await client.get(f"/api/v1/usuarios/{usuario_id}/paineis")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2
        # Verificar que todos os painéis pertencem ao usuário correto
        for painel in data["data"]:
            assert painel["usuario_id"] == usuario_id


@pytest.mark.asyncio
async def test_list_paineis_with_filters(setup_usuario):
    """Testa listagem de painéis com filtros"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar painéis com nomes específicos
        await client.post("/api/v1/paineis", json={
            "nome": "Painel Casa",
            "descricao": "Gastos da casa",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        await client.post("/api/v1/paineis", json={
            "nome": "Painel Trabalho",
            "descricao": "Gastos do trabalho",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        # Listar com filtro por nome
        response = await client.get(f"/api/v1/usuarios/{usuario_id}/paineis?nome=Casa")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "PAINEL_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        # Verificar que todos os painéis contêm "Casa" no nome
        for painel in data["data"]:
            assert "Casa" in painel["nome"]


@pytest.mark.asyncio
async def test_create_painel_duplicate_name(setup_usuario):
    """Testa criação de painel com nome duplicado para o mesmo usuário"""
    usuario_id = await setup_usuario()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar primeiro painel
        await client.post("/api/v1/paineis", json={
            "nome": "Painel Duplicado",
            "descricao": "Primeiro painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        # Tentar criar segundo painel com mesmo nome para mesmo usuário
        response = await client.post("/api/v1/paineis", json={
            "nome": "Painel Duplicado",
            "descricao": "Segundo painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })

        assert response.status_code == 400  # Deve falhar por violação de constraint única
        data = response.json()
        assert data["code"] == "DATABASE_ERROR"


@pytest.mark.asyncio
async def test_create_painel_same_name_different_users():
    """Testa criação de painéis com mesmo nome para usuários diferentes"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar dois usuários
        usuario1_response = await client.post("/api/v1/usuarios", json={
            "nome": "Usuário 1",
            "email": "user1@example.com"
        })
        usuario1_id = usuario1_response.json()["data"]["id"]

        usuario2_response = await client.post("/api/v1/usuarios", json={
            "nome": "Usuário 2",
            "email": "user2@example.com"
        })
        usuario2_id = usuario2_response.json()["data"]["id"]

        # Criar painéis com mesmo nome para usuários diferentes
        response1 = await client.post("/api/v1/paineis", json={
            "nome": "Painel Casa",
            "descricao": "Painel do usuário 1",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario1_id
        })
        assert response1.status_code == 201

        response2 = await client.post("/api/v1/paineis", json={
            "nome": "Painel Casa",
            "descricao": "Painel do usuário 2",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario2_id
        })
        assert response2.status_code == 201  # Deve ser permitido


@pytest.mark.asyncio
async def test_delete_usuario_cascades_paineis():
    """Testa que deletar usuário remove seus painéis (CASCADE)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar usuário
        usuario_response = await client.post("/api/v1/usuarios", json={
            "nome": "Usuário Para Deletar",
            "email": "deletar@example.com"
        })
        usuario_id = usuario_response.json()["data"]["id"]

        # Criar painéis para o usuário
        painel1_response = await client.post("/api/v1/paineis", json={
            "nome": "Painel 1",
            "descricao": "Primeiro painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        painel1_id = painel1_response.json()["data"]["id"]

        painel2_response = await client.post("/api/v1/paineis", json={
            "nome": "Painel 2",
            "descricao": "Segundo painel",
            "tipo_conta": "CARTAO_CREDITO",
            "usuario_id": usuario_id
        })
        painel2_id = painel2_response.json()["data"]["id"]

        # Deletar usuário
        delete_response = await client.delete(f"/api/v1/usuarios/{usuario_id}")
        assert delete_response.status_code == 200

        # Verificar que os painéis também foram deletados
        painel1_response = await client.get(f"/api/v1/paineis/{painel1_id}")
        assert painel1_response.status_code == 404

        painel2_response = await client.get(f"/api/v1/paineis/{painel2_id}")
        assert painel2_response.status_code == 404
