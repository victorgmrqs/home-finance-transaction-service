"""
Testes unitários para HealthcheckService
"""
from unittest.mock import AsyncMock

import pytest

from src.application.healthcheck_service import HealthcheckService


@pytest.fixture
def mock_repository():
    """Mock do repository de healthcheck"""
    return AsyncMock()


@pytest.mark.asyncio
async def test_healthcheck_when_database_is_healthy(mock_repository):
    """Testa healthcheck quando banco está saudável"""
    # Arrange
    mock_repository.check_db.return_value = {
        "status": "OK",
        "db_response_time": 5.2
    }
    service = HealthcheckService(mock_repository)

    # Act
    result = await service.run()

    # Assert
    assert result["status"] == "healthy"
    assert result["database_status"] == "OK"
    assert result["version"] == "0.1.0"
    assert result["environment"] == "development"
    assert "timestamp" in result
    assert "uptime_seconds" in result
    assert result["uptime_seconds"] >= 0
    assert result["database"]["status"] == "OK"
    assert result["database"]["db_response_time"] == 5.2


@pytest.mark.asyncio
async def test_healthcheck_when_database_is_unhealthy(mock_repository):
    """Testa healthcheck quando banco está com problemas"""
    # Arrange
    mock_repository.check_db.return_value = {
        "status": "ERROR",
        "error": "Connection refused"
    }
    service = HealthcheckService(mock_repository)

    # Act
    result = await service.run()

    # Assert
    assert result["status"] == "unhealthy"
    assert result["database_status"] == "ERROR"
    assert result["database"]["status"] == "ERROR"
    assert result["database"]["error"] == "Connection refused"


@pytest.mark.asyncio
async def test_healthcheck_uptime_increases(mock_repository):
    """Testa que uptime aumenta entre chamadas"""
    # Arrange
    mock_repository.check_db.return_value = {
        "status": "OK",
        "db_response_time": 1.0
    }
    service = HealthcheckService(mock_repository)

    # Act
    result1 = await service.run()
    import asyncio
    await asyncio.sleep(0.1)  # Wait 100ms
    result2 = await service.run()

    # Assert
    assert result2["uptime_seconds"] > result1["uptime_seconds"]
