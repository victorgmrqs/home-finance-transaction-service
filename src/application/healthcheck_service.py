
from src.ports.healthcheck_port import IHealthcheckRepository

class HealthcheckService:
    def __init__(self, repository: IHealthcheckRepository):
        self.repository = repository

    async def run(self) -> dict:
        db_status = await self.repository.check_db()
        return {
            "database": db_status,
            "service": "transaction-service"
        }
