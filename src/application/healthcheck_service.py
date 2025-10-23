"""
Healthcheck Service
Serviço de verificação de saúde da aplicação
"""

import time
from datetime import datetime, timezone
from src.ports.healthcheck_port import IHealthcheckRepository
from src.core.config import settings


class HealthcheckService:
    """
    Serviço de healthcheck da aplicação

    Mantém estado do tempo de inicialização para calcular uptime
    """
    start_time = time.time()

    def __init__(self, repository: IHealthcheckRepository):
        self.repository = repository

    async def run(self) -> dict:
        """
        Executa verificação de saúde completa

        Returns:
            dict: Informações de saúde incluindo status, uptime, versão e database
        """
        db_status = await self.repository.check_db()
        uptime = time.time() - self.start_time

        return {
            "status": "healthy" if db_status["status"] == "OK" else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.app_version,
            "environment": settings.environment,
            "database_status": db_status["status"],
            "uptime_seconds": round(uptime, 2),
            "database": db_status
        }
