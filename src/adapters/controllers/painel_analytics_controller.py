"""
Painel Analytics Controller
Endpoints HTTP para análises e estatísticas de painéis
"""

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from src.db.session import get_session
from src.adapters.repositories.painel_repository import PainelRepository
from src.adapters.repositories.transaction_repository import TransactionRepository
from src.application.painel_service import PainelService
from src.adapters.middlewares.auth_middleware import get_current_user_id
from src.shared.responses import success_response

router = APIRouter(tags=["Painéis - Analytics"])


@router.get("/paineis/{id}/balanco", response_model=None)
async def get_painel_balanco(
    request: Request,
    id: int,
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Calcula o balanço de um painel

    **Requer autenticação** (header X-User-ID em dev)

    Parâmetros:
    - **id**: ID do painel
    - **data_inicio**: Data inicial do período (opcional)
    - **data_fim**: Data final do período (opcional)

    Retorna:
    - **total_entradas**: Soma de todas as entradas
    - **total_saidas**: Soma de todas as saídas
    - **saldo**: Diferença entre entradas e saídas
    - **quantidade_transacoes**: Total de transações no período
    """
    painel_repository = PainelRepository(session)
    transaction_repository = TransactionRepository(session)
    service = PainelService(painel_repository, transaction_repository)

    try:
        balanco = await service.calcular_balanco(
            painel_id=id,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        return success_response(
            code="BALANCO_CALCULADO",
            message="Balanço calculado com sucesso",
            data=balanco
        )
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PAINEL_NOT_FOUND",
                "message": str(e),
                "data": None
            }
        )
