"""
Testes de integração para endpoint /health
"""
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_health_check_returns_200_when_healthy():
    """Testa que health check retorna 200 quando sistema está saudável"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["code"] == "HEALTHCHECK_OK"
        assert data["message"] == "Service is healthy"
        assert data["data"]["status"] == "healthy"
        assert data["data"]["database_status"] == "OK"
        assert "timestamp" in data["data"]
        assert "version" in data["data"]
        assert "environment" in data["data"]
        assert "uptime_seconds" in data["data"]
        assert data["data"]["database"]["status"] == "OK"
        assert "db_response_time" in data["data"]["database"]


@pytest.mark.asyncio
async def test_health_check_returns_503_when_database_fails():
    """Testa que health check retorna 503 quando banco falha"""
    with patch(
        "src.adapters.repositories.healthcheck_repository.HealthCheckRepository.check_db"
    ) as mock_check_db:
        # Simular falha no banco
        mock_check_db.return_value = {
            "status": "ERROR",
            "error": "Database connection failed"
        }

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")

            assert response.status_code == 503
            data = response.json()

            assert data["code"] == "HEALTHCHECK_FAIL"
            assert data["message"] == "Database connection failed"


@pytest.mark.asyncio
async def test_health_check_response_structure():
    """Testa estrutura completa da resposta do health check"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/health")
        data = response.json()

        # Verificar estrutura base
        assert "code" in data
        assert "message" in data
        assert "data" in data

        # Verificar estrutura de dados
        health_data = data["data"]
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "version" in health_data
        assert "environment" in health_data
        assert "database_status" in health_data
        assert "uptime_seconds" in health_data
        assert "database" in health_data

        # Verificar estrutura de database
        db_data = health_data["database"]
        assert "status" in db_data


@pytest.mark.asyncio
async def test_health_check_performance():
    """Testa que health check responde rapidamente (< 100ms)"""
    import time

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        start = time.perf_counter()
        response = await client.get("/health")
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 100, f"Health check took {elapsed:.2f}ms (should be < 100ms)"
