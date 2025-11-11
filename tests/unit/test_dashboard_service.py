"""
Testes unitários para o Dashboard Service
"""

from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from src.application.dashboard_service import DashboardService


@pytest.mark.asyncio
async def test_get_dashboard_summary_success():
    """Testa busca de dashboard summary com sucesso"""
    # Arrange
    mock_repository = Mock()
    mock_repository.get_resumo_geral = AsyncMock(return_value={
        "total_receitas": 11000.00,
        "total_despesas": 925.00,
        "saldo": 10075.00,
        "total_transacoes": 8
    })
    mock_repository.get_agregacao_por_categoria = AsyncMock(return_value=[
        {"categoria": "Alimentação", "total": 600.00, "quantidade": 2, "percentual": 64.9},
        {"categoria": "Transporte", "total": 245.00, "quantidade": 2, "percentual": 26.5},
    ])
    mock_repository.get_agregacao_por_painel = AsyncMock(return_value=[
        {"painel_id": 1, "painel_nome": "Pessoal", "tipo_conta": "CONTA_BANCARIA", "total_receitas": 6500.00, "total_despesas": 475.00, "saldo": 6025.00, "quantidade_transacoes": 5},
        {"painel_id": 2, "painel_nome": "Casal", "tipo_conta": "CARTAO_CREDITO", "total_receitas": 4500.00, "total_despesas": 450.00, "saldo": 4050.00, "quantidade_transacoes": 3},
    ])
    mock_repository.get_estatisticas = AsyncMock(return_value={
        "transacao_min": 45.00,
        "transacao_max": 5000.00,
        "media_diaria": 185.00,
        "maior_despesa": 5000.00,
        "menor_despesa": 45.00,
        "maior_receita": 5000.00,
        "menor_receita": 45.00
    })

    service = DashboardService(mock_repository)

    # Act
    result = await service.get_dashboard_summary(usuario_id=1)

    # Assert
    assert result is not None
    assert result["resumo"]["total_receitas"] == 11000.00
    assert result["resumo"]["total_despesas"] == 925.00
    assert result["resumo"]["saldo"] == 10075.00
    assert result["resumo"]["total_transacoes"] == 8

    assert len(result["por_categoria"]) == 2
    assert result["por_categoria"][0]["categoria"] == "Alimentação"
    assert result["por_categoria"][0]["total"] == 600.00

    assert len(result["por_painel"]) == 2
    assert result["por_painel"][0]["painel_nome"] == "Pessoal"
    assert result["por_painel"][0]["saldo"] == 6025.00

    assert result["estatisticas"]["transacao_min"] == 45.00
    assert result["estatisticas"]["transacao_max"] == 5000.00
    assert result["estatisticas"]["media_diaria"] == 185.00

    # Verify repository calls
    mock_repository.get_resumo_geral.assert_called_once_with(1, None, None, None)
    mock_repository.get_agregacao_por_categoria.assert_called_once_with(1, None, None, None)
    mock_repository.get_agregacao_por_painel.assert_called_once_with(1, None, None, None)
    mock_repository.get_estatisticas.assert_called_once_with(1, None, None, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_with_date_filters():
    """Testa busca de dashboard summary com filtros de data"""
    # Arrange
    mock_repository = Mock()
    mock_repository.get_resumo_geral = AsyncMock(return_value={
        "total_receitas": 6500.00,
        "total_despesas": 475.00,
        "saldo": 6025.00,
        "total_transacoes": 6
    })
    mock_repository.get_agregacao_por_categoria = AsyncMock(return_value=[])
    mock_repository.get_agregacao_por_painel = AsyncMock(return_value=[])
    mock_repository.get_estatisticas = AsyncMock(return_value={
        "transacao_min": 45.00,
        "transacao_max": 5000.00,
        "media_diaria": 95.00
    })

    service = DashboardService(mock_repository)
    data_inicio = date(2025, 11, 1)
    data_fim = date(2025, 11, 5)

    # Act
    result = await service.get_dashboard_summary(
        usuario_id=1,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    # Assert
    assert result is not None
    assert result["resumo"]["total_transacoes"] == 6

    # Verify repository calls with date filters
    mock_repository.get_resumo_geral.assert_called_once_with(1, data_inicio, data_fim, None)
    mock_repository.get_agregacao_por_categoria.assert_called_once_with(1, data_inicio, data_fim, None)
    mock_repository.get_agregacao_por_painel.assert_called_once_with(1, data_inicio, data_fim, None)
    mock_repository.get_estatisticas.assert_called_once_with(1, data_inicio, data_fim, None)


@pytest.mark.asyncio
async def test_get_dashboard_summary_with_painel_filter():
    """Testa busca de dashboard summary com filtro de painéis"""
    # Arrange
    mock_repository = Mock()
    mock_repository.get_resumo_geral = AsyncMock(return_value={
        "total_receitas": 6500.00,
        "total_despesas": 475.00,
        "saldo": 6025.00,
        "total_transacoes": 5
    })
    mock_repository.get_agregacao_por_categoria = AsyncMock(return_value=[])
    mock_repository.get_agregacao_por_painel = AsyncMock(return_value=[
        {"painel_id": 1, "painel_nome": "Pessoal", "tipo_conta": "CONTA_BANCARIA", "total_receitas": 6500.00, "total_despesas": 475.00, "saldo": 6025.00, "quantidade_transacoes": 5}
    ])
    mock_repository.get_estatisticas = AsyncMock(return_value={
        "transacao_min": 45.00,
        "transacao_max": 5000.00,
        "media_diaria": 95.00
    })

    service = DashboardService(mock_repository)
    painel_ids = [1]

    # Act
    result = await service.get_dashboard_summary(
        usuario_id=1,
        painel_ids=painel_ids
    )

    # Assert
    assert result is not None
    assert result["resumo"]["total_transacoes"] == 5
    assert len(result["por_painel"]) == 1
    assert result["por_painel"][0]["painel_nome"] == "Pessoal"

    # Verify repository calls with painel filter
    mock_repository.get_resumo_geral.assert_called_once_with(1, None, None, painel_ids)
    mock_repository.get_agregacao_por_categoria.assert_called_once_with(1, None, None, painel_ids)
    mock_repository.get_agregacao_por_painel.assert_called_once_with(1, None, None, painel_ids)
    mock_repository.get_estatisticas.assert_called_once_with(1, None, None, painel_ids)


@pytest.mark.asyncio
async def test_get_dashboard_summary_empty_results():
    """Testa busca de dashboard summary com resultados vazios"""
    # Arrange
    mock_repository = Mock()
    mock_repository.get_resumo_geral = AsyncMock(return_value={
        "total_receitas": 0.00,
        "total_despesas": 0.00,
        "saldo": 0.00,
        "total_transacoes": 0
    })
    mock_repository.get_agregacao_por_categoria = AsyncMock(return_value=[])
    mock_repository.get_agregacao_por_painel = AsyncMock(return_value=[])
    mock_repository.get_estatisticas = AsyncMock(return_value={
        "transacao_min": 0.00,
        "transacao_max": 0.00,
        "media_diaria": 0.00,
        "maior_despesa": 0.00,
        "menor_despesa": 0.00,
        "maior_receita": 0.00,
        "menor_receita": 0.00
    })

    service = DashboardService(mock_repository)

    # Act
    result = await service.get_dashboard_summary(usuario_id=999)

    # Assert
    assert result is not None
    assert result["resumo"]["total_transacoes"] == 0
    assert result["resumo"]["saldo"] == 0.00
    assert len(result["por_categoria"]) == 0
    assert len(result["por_painel"]) == 0


@pytest.mark.asyncio
async def test_get_dashboard_summary_all_filters_combined():
    """Testa busca de dashboard summary com todos os filtros combinados"""
    # Arrange
    mock_repository = Mock()
    mock_repository.get_resumo_geral = AsyncMock(return_value={
        "total_receitas": 1500.00,
        "total_despesas": 200.00,
        "saldo": 1300.00,
        "total_transacoes": 3
    })
    mock_repository.get_agregacao_por_categoria = AsyncMock(return_value=[
        {"categoria": "Freelance", "total": 1500.00, "quantidade": 1, "percentual": 100.0}
    ])
    mock_repository.get_agregacao_por_painel = AsyncMock(return_value=[
        {"painel_id": 1, "painel_nome": "Pessoal", "tipo_conta": "CONTA_BANCARIA", "total_receitas": 1500.00, "total_despesas": 200.00, "saldo": 1300.00, "quantidade_transacoes": 3}
    ])
    mock_repository.get_estatisticas = AsyncMock(return_value={
        "transacao_min": 50.00,
        "transacao_max": 1500.00,
        "media_diaria": 100.00,
        "maior_despesa": 1500.00,
        "menor_despesa": 50.00,
        "maior_receita": 1500.00,
        "menor_receita": 50.00
    })

    service = DashboardService(mock_repository)
    data_inicio = date(2025, 11, 1)
    data_fim = date(2025, 11, 3)
    painel_ids = [1]

    # Act
    result = await service.get_dashboard_summary(
        usuario_id=1,
        data_inicio=data_inicio,
        data_fim=data_fim,
        painel_ids=painel_ids
    )

    # Assert
    assert result is not None
    assert result["resumo"]["total_transacoes"] == 3

    # Verify all filters were passed to repository
    mock_repository.get_resumo_geral.assert_called_once_with(1, data_inicio, data_fim, painel_ids)
    mock_repository.get_agregacao_por_categoria.assert_called_once_with(1, data_inicio, data_fim, painel_ids)
    mock_repository.get_agregacao_por_painel.assert_called_once_with(1, data_inicio, data_fim, painel_ids)
    mock_repository.get_estatisticas.assert_called_once_with(1, data_inicio, data_fim, painel_ids)
