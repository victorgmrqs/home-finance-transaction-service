"""
Testes de integração para API de transações
"""


import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def setup_test_data():
    """Setup inicial: cria usuário e painel para os testes"""
    async def _setup():
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Criar usuário
            usuario_response = await client.post("/api/v1/usuarios", json={
                "nome": "Usuário Teste",
                "email": "teste@example.com"
            })
            usuario_id = usuario_response.json()["data"]["id"]

            # Criar painel
            painel_response = await client.post("/api/v1/paineis", json={
                "nome": "Painel Teste",
                "descricao": "Painel para testes",
                "tipo_conta": "CARTAO_CREDITO",
                "usuario_id": usuario_id
            })
            painel_id = painel_response.json()["data"]["id"]

            return {"usuario_id": usuario_id, "painel_id": painel_id}

    return _setup


@pytest.mark.asyncio
async def test_create_transaction(setup_test_data):
    """Testa criação de transação via API"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Salário",
            "valor": 5000.00,
            "tipo": "ENTRADA",
            "categoria": "salario",
            "painel_id": test_data["painel_id"]
        })

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "TRANSACTION_CREATED"
        assert data["message"] == "Transação criada com sucesso"
        assert data["data"]["descricao"] == "Salário"
        assert data["data"]["valor"] == 5000.00
        assert data["data"]["tipo"] == "ENTRADA"


@pytest.mark.asyncio
async def test_list_transactions(setup_test_data):
    """Testa listagem de transações"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar transação primeiro
        await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Compra mercado",
            "valor": 150.50,
            "tipo": "SAIDA",
            "categoria": "alimentacao",
            "painel_id": test_data["painel_id"]
        })

        # Listar
        response = await client.get(f"/api/v1/transactions?painel_id={test_data['painel_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TRANSACTION_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_get_transaction(setup_test_data):
    """Testa busca de transação por ID"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Teste",
            "valor": 100.00,
            "tipo": "SAIDA",
            "categoria": "teste",
            "painel_id": test_data["painel_id"]
        })
        created_id = create_response.json()["data"]["id"]

        # Buscar
        response = await client.get(f"/api/v1/transactions/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TRANSACTION_DETAIL_SUCCESS"
        assert data["data"]["id"] == created_id


@pytest.mark.asyncio
async def test_update_transaction(setup_test_data):
    """Testa atualização de transação"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Original",
            "valor": 100.00,
            "tipo": "SAIDA",
            "categoria": "teste",
            "painel_id": test_data["painel_id"]
        })
        created_id = create_response.json()["data"]["id"]

        # Atualizar
        response = await client.put(f"/api/v1/transactions/{created_id}", json={
            "descricao": "Atualizado"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TRANSACTION_UPDATED"
        assert data["data"]["descricao"] == "Atualizado"


@pytest.mark.asyncio
async def test_delete_transaction(setup_test_data):
    """Testa remoção de transação"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar
        create_response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Para deletar",
            "valor": 100.00,
            "tipo": "SAIDA",
            "categoria": "teste",
            "painel_id": test_data["painel_id"]
        })
        created_id = create_response.json()["data"]["id"]

        # Deletar
        response = await client.delete(f"/api/v1/transactions/{created_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TRANSACTION_DELETED"

        # Verificar que foi deletado
        get_response = await client.get(f"/api/v1/transactions/{created_id}")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_transaction_invalid_data(setup_test_data):
    """Testa criação com dados inválidos"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "",  # Descrição vazia (inválido)
            "valor": 100.00,
            "tipo": "SAIDA",
            "categoria": "teste",
            "painel_id": test_data["painel_id"]
        })

        assert response.status_code == 422  # Validation error do Pydantic


@pytest.mark.asyncio
async def test_create_transaction_without_painel_id():
    """Testa criação de transação sem painel_id (deve falhar)"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Teste sem painel",
            "valor": 100.00,
            "tipo": "SAIDA",
            "categoria": "teste"
            # Sem painel_id - deve falhar
        })

        assert response.status_code == 422  # Validation error do Pydantic


@pytest.mark.asyncio
async def test_list_transactions_with_painel_filter(setup_test_data):
    """Testa listagem de transações com filtro por painel"""
    test_data = await setup_test_data()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Criar transação
        await client.post("/api/v1/transactions", json={
            "data": "2025-01-15",
            "descricao": "Transação no painel específico",
            "valor": 200.00,
            "tipo": "ENTRADA",
            "categoria": "teste",
            "painel_id": test_data["painel_id"]
        })

        # Listar com filtro por painel
        response = await client.get(f"/api/v1/transactions?painel_id={test_data['painel_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TRANSACTION_LIST_SUCCESS"
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        # Verificar que todas as transações pertencem ao painel correto
        for transaction in data["data"]:
            assert transaction["painel_id"] == test_data["painel_id"]
