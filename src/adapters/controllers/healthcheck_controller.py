from fastapi import APIRouter, Depends
from src.application.healthcheck_service import HealthcheckService
from src.adapters.repositories.healthcheck_repository import HealthCheckRepository
from src.adapters.presenters.healthcheck_presenter import present_healthcheck
from src.db.session import get_session  # factory do SQLAlchemy Session

router = APIRouter()

@router.get("/health", tags=["Health"])
async def healthcheck(session=Depends(get_session)):
    repo = HealthCheckRepository(session)
    service = HealthcheckService(repo)
    result = await service.run()
    return present_healthcheck(result)
