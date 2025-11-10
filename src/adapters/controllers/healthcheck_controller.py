from fastapi import APIRouter, Depends, Response, status

from src.adapters.presenters.healthcheck_presenter import present_healthcheck
from src.adapters.repositories.healthcheck_repository import HealthCheckRepository
from src.application.healthcheck_service import HealthcheckService
from src.db.session import get_session  # factory do SQLAlchemy Session

router = APIRouter()

@router.get("/health", tags=["Health"])
async def healthcheck(response: Response, session=Depends(get_session)):
    """
    Health check endpoint para verificar saúde do serviço

    Verifica:
    - Conexão com banco de dados
    - Uptime do serviço
    - Versão da aplicação

    Returns:
        - 200 OK: Serviço saudável
        - 503 Service Unavailable: Serviço com problemas
    """
    repo = HealthCheckRepository(session)
    service = HealthcheckService(repo)
    result = await service.run()

    # Definir status HTTP correto baseado no resultado
    if result["status"] != "healthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return present_healthcheck(result)
