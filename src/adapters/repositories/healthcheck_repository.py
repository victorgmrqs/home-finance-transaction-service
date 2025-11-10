import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.ports.healthcheck_port import IHealthcheckRepository


class HealthCheckRepository(IHealthcheckRepository):
    def __init__(self, session: AsyncSession):
        self.session = session


    async def check_db(self) -> dict:
        start_time = time.perf_counter()
        try:
            query = 'SELECT 1'
            await self.session.execute(text(query))
            elapsed_time = (time.perf_counter() - start_time) * 1000
            return {
                'status': 'OK',
                'db_response_time': round(elapsed_time, 2),
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
            }
