"""
Testes de integração para o endpoint de Dashboard
"""

from datetime import UTC, date, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from src.adapters.repositories.models import (
    PainelModel,
    TransactionModel,
    UsuarioModel,
)
from src.db.session import get_session
from src.main import app


@pytest.mark.asyncio
async def test_get_dashboard_summary_success(test_db_session):
    """Testa GET /api/v1/dashboard/summary com sucesso"""
    # Sobrescrever dependência get_session para usar a sessão de teste
    async def override_get_session():
        yield test_db_session
    app.dependency_overrides[get_session] = override_get_session
    
    # Arrange: Criar dados de teste
    usuario = UsuarioModel(
        id=100,
        nome="Dashboard Test User",
        email="dashboard@test.com",
        password_hash="hash123",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(usuario)

    painel = PainelModel(
        id=100,
        nome="Painel Test",
        usuario_id=100,
        tipo_conta="CONTA_BANCARIA",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(painel)

    transactions = [
        TransactionModel(
            id=100,
            data=date(2025, 11, 1),
            descricao="Salário",
            valor=5000.00,
            tipo="ENTRADA",
            categoria="Salário",
            painel_id=100,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
        TransactionModel(
            id=101,
            data=date(2025, 11, 2),
            descricao="Mercado",
            valor=300.00,
            tipo="SAIDA",
            categoria="Alimentação",
            painel_id=100,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
        TransactionModel(
            id=102,
            data=date(2025, 11, 3),
            descricao="Uber",
            valor=50.00,
            tipo="SAIDA",
            categoria="Transporte",
            painel_id=100,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
    ]
    for transaction in transactions:
        test_db_session.add(transaction)

    await test_db_session.commit()

    # Act
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/dashboard/summary",
            headers={"X-User-ID": "100"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["code"] == "DASHBOARD_SUMMARY_SUCCESS"
    assert data["message"] == "Dashboard summary retrieved successfully"
    assert data["data"] is not None

    # Verify resumo
    resumo = data["data"]["resumo"]
    assert resumo["total_receitas"] == 5000.00
    assert resumo["total_despesas"] == 350.00
    assert resumo["saldo"] == 4650.00
    assert resumo["total_transacoes"] == 3

    # Verify categorias
    categorias = data["data"]["por_categoria"]
    assert len(categorias) == 2
    assert categorias[0]["categoria"] in ["Alimentação", "Transporte"]

    # Verify paineis
    paineis = data["data"]["por_painel"]
    assert len(paineis) == 1
    assert paineis[0]["painel_nome"] == "Painel Test"
    assert paineis[0]["total_receitas"] == 5000.00
    assert paineis[0]["total_despesas"] == 350.00
    assert paineis[0]["saldo"] == 4650.00

    # Verify estatisticas
    estatisticas = data["data"]["estatisticas"]
    assert estatisticas["transacao_min"] == 50.00
    assert estatisticas["transacao_max"] == 5000.00
    assert estatisticas["media_diaria"] > 0
    
    # Limpar override
    app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_with_date_filters(test_db_session):
    """Testa GET /api/v1/dashboard/summary com filtros de data"""
    # Sobrescrever dependência get_session para usar a sessão de teste
    async def override_get_session():
        yield test_db_session
    app.dependency_overrides[get_session] = override_get_session
    
    # Arrange
    usuario = UsuarioModel(
        id=101,
        nome="Filter Test User",
        email="filter@test.com",
        password_hash="hash123",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(usuario)

    painel = PainelModel(
        id=101,
        nome="Painel Filter",
        usuario_id=101,
        tipo_conta="CONTA_BANCARIA",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(painel)

    transactions = [
        TransactionModel(
            id=200,
            data=date(2025, 10, 15),  # Fora do range
            descricao="Transação antiga",
            valor=1000.00,
            tipo="ENTRADA",
            categoria="Salário",
            painel_id=101,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
        TransactionModel(
            id=201,
            data=date(2025, 11, 2),  # Dentro do range
            descricao="Transação nova",
            valor=500.00,
            tipo="ENTRADA",
            categoria="Freelance",
            painel_id=101,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
    ]
    for transaction in transactions:
        test_db_session.add(transaction)

    await test_db_session.commit()

    # Act
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/dashboard/summary?data_inicio=2025-11-01&data_fim=2025-11-30",
            headers={"X-User-ID": "101"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()

    resumo = data["data"]["resumo"]
    # Deve conter apenas a transação de novembro
    assert resumo["total_receitas"] == 500.00
    assert resumo["total_transacoes"] == 1
    
    # Limpar override
    app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_with_painel_filter(test_db_session):
    """Testa GET /api/v1/dashboard/summary com filtro de painéis"""
    # Sobrescrever dependência get_session para usar a sessão de teste
    async def override_get_session():
        yield test_db_session
    app.dependency_overrides[get_session] = override_get_session
    
    # Arrange
    usuario = UsuarioModel(
        id=102,
        nome="Painel Filter User",
        email="painel@test.com",
        password_hash="hash123",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(usuario)

    painel1 = PainelModel(
        id=201,
        nome="Painel 1",
        usuario_id=102,
        tipo_conta="CONTA_BANCARIA",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    painel2 = PainelModel(
        id=202,
        nome="Painel 2",
        usuario_id=102,
        tipo_conta="CARTAO_CREDITO",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add_all([painel1, painel2])

    transactions = [
        TransactionModel(
            id=300,
            data=date(2025, 11, 1),
            descricao="Painel 1",
            valor=1000.00,
            tipo="ENTRADA",
            categoria="Salário",
            painel_id=201,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
        TransactionModel(
            id=301,
            data=date(2025, 11, 1),
            descricao="Painel 2",
            valor=500.00,
            tipo="ENTRADA",
            categoria="Freelance",
            painel_id=202,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC)
        ),
    ]
    for transaction in transactions:
        test_db_session.add(transaction)

    await test_db_session.commit()

    # Act: Filtrar apenas painel 201
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/dashboard/summary?painel_ids=201",
            headers={"X-User-ID": "102"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()

    resumo = data["data"]["resumo"]
    assert resumo["total_receitas"] == 1000.00
    assert resumo["total_transacoes"] == 1

    paineis = data["data"]["por_painel"]
    assert len(paineis) == 1
    assert paineis[0]["painel_nome"] == "Painel 1"
    
    # Limpar override
    app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_empty_results(test_db_session):
    """Testa GET /api/v1/dashboard/summary com usuário sem dados"""
    # Sobrescrever dependência get_session para usar a sessão de teste
    async def override_get_session():
        yield test_db_session
    app.dependency_overrides[get_session] = override_get_session
    
    # Arrange: Criar apenas usuário sem painéis/transações
    usuario = UsuarioModel(
        id=103,
        nome="Empty User",
        email="empty@test.com",
        password_hash="hash123",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(usuario)
    await test_db_session.commit()

    # Act
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/dashboard/summary",
            headers={"X-User-ID": "103"}
        )

    # Assert
    assert response.status_code == 200
    data = response.json()

    resumo = data["data"]["resumo"]
    assert resumo["total_receitas"] == 0.00
    assert resumo["total_despesas"] == 0.00
    assert resumo["saldo"] == 0.00
    assert resumo["total_transacoes"] == 0

    assert len(data["data"]["por_categoria"]) == 0
    assert len(data["data"]["por_painel"]) == 0
    
    # Limpar override
    app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_rate_limiting(test_db_session):
    """Testa rate limiting do endpoint (30/minuto)"""
    # Sobrescrever dependência get_session para usar a sessão de teste
    async def override_get_session():
        yield test_db_session
    app.dependency_overrides[get_session] = override_get_session
    
    # Arrange: Criar usuário
    usuario = UsuarioModel(
        id=104,
        nome="Rate Test User",
        email="rate@test.com",
        password_hash="hash123",
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC)
    )
    test_db_session.add(usuario)
    await test_db_session.commit()

    # Act: Fazer múltiplas requisições
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        responses = []
        for _ in range(5):  # Testar com 5 requisições (bem abaixo do limite de 30)
            response = await client.get(
                "/api/v1/dashboard/summary",
                headers={"X-User-ID": "104"}
            )
            responses.append(response)

    # Assert: Todas devem ter sucesso (abaixo do limite)
    for response in responses:
        assert response.status_code == 200
    
    # Limpar override
    app.dependency_overrides.pop(get_session, None)
