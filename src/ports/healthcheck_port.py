from abc import ABC, abstractmethod


class IHealthcheckRepository(ABC):
    @abstractmethod
    async def check_db(self) -> dict:
        """Verifica status do banco e retorna métricas básicas"""
        pass
