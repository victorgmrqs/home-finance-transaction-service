"""
Transaction Controller
Endpoints HTTP para gerenciamento de transações
"""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from calendar import monthrange

from src.db.session import get_session
from src.adapters.repositories.transaction_repository import TransactionRepository
from src.application.transaction_service import TransactionService
from src.adapters.presenters.transaction_presenter import (
    present_transaction_created,
    present_transaction_detail,
    present_transaction_list,
    present_transaction_updated,
    present_transaction_deleted
)
from src.core.schemas_api import (
    TransactionCreateRequest, 
    TransactionUpdateRequest,
    TransactionCreateResponse,
    TransactionDetailResponse,
    TransactionListResponse,
    TransactionUpdateResponse,
    TransactionDeleteResponse
)
from src.domain.models.transaction import Transaction, TransactionType, Recurrence, TipoDivisao
from src.adapters.middlewares.auth_middleware import get_current_user_id

router = APIRouter(tags=["Transactions"])


@router.post("/transactions", status_code=status.HTTP_201_CREATED, response_model=TransactionCreateResponse)
async def create_transaction(
    req: Request,
    request: TransactionCreateRequest,
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Cria uma nova transação

    **Requer autenticação** (header X-User-ID em dev)

    - **data**: Data da transação
    - **descricao**: Descrição da transação
    - **valor**: Valor (deve ser positivo)
    - **tipo**: ENTRADA ou SAIDA
    - **categoria**: Categoria da transação
    - **recorrencia**: (Opcional) DIARIO, SEMANAL, MENSAL ou OCASIONAL
    - **parcelas**: (Opcional) Número de parcelas
    - **local_id**: (Opcional) ID do local
    - **painel_id**: ID do painel (obrigatório)
    """
    # Converter request para entidade de domínio
    transaction = Transaction(
        id=None,
        data=request.data,
        descricao=request.descricao,
        valor=request.valor,
        tipo=TransactionType(request.tipo),
        categoria=request.categoria,
        recorrencia=Recurrence(request.recorrencia) if request.recorrencia else None,
        parcelas=request.parcelas,
        tipo_divisao=TipoDivisao(request.tipo_divisao) if request.tipo_divisao else TipoDivisao.PESSOAL,
        valor_por_pessoa=request.valor_por_pessoa,
        porcentagem_divisao=request.porcentagem_divisao,
        local_id=request.local_id,
        painel_id=request.painel_id,
        # Campos de parcelamento e recorrência (valores padrão para nova transação)
        parcela_numero=None,
        transacao_mae_id=None,
        eh_parcela=False,
        transacao_recorrente_origem_id=None,
        recorrencia_ativa=True,
        proxima_geracao=None
    )

    # Executar caso de uso
    repository = TransactionRepository(session)
    service = TransactionService(repository)
    created = await service.create_transaction(transaction)

    return present_transaction_created(created)


@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    request: Request,
    painel_id: int = Query(..., description="ID do painel (obrigatório)"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamanho da página"),
    tipo: Optional[str] = Query(None, pattern="^(ENTRADA|SAIDA)$", description="Filtrar por tipo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    local_id: Optional[int] = Query(None, description="Filtrar por ID do local"),
    mes: Optional[str] = Query(None, pattern="^\\d{4}-\\d{2}$", description="Filtrar por mês (YYYY-MM)"),
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    descricao: Optional[str] = Query(None, description="Buscar por descrição"),
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Lista transações com filtros e paginação

    **Requer autenticação** (header X-User-ID em dev)

    Parâmetros de query:
    - **painel_id**: ID do painel (obrigatório)
    - **page**: Número da página (padrão: 1)
    - **page_size**: Tamanho da página (padrão: 50, máx: 100)
    - **tipo**: Filtrar por ENTRADA ou SAIDA
    - **categoria**: Filtrar por categoria
    - **local_id**: Filtrar por ID do local
    - **mes**: Filtrar por mês (formato: YYYY-MM, ex: 2025-09)
    - **data_inicio**: Data inicial do filtro (formato: YYYY-MM-DD)
    - **data_fim**: Data final do filtro (formato: YYYY-MM-DD)
    - **descricao**: Buscar por texto na descrição

    Nota: Se 'mes' for fornecido, ele sobrescreve data_inicio e data_fim
    """
    repository = TransactionRepository(session)
    service = TransactionService(repository)

    # Se mes for fornecido, calcular data_inicio e data_fim automaticamente
    if mes:
        ano, mes_numero = mes.split('-')
        ano_int = int(ano)
        mes_int = int(mes_numero)

        # Primeiro dia do mês
        data_inicio = date(ano_int, mes_int, 1)

        # Último dia do mês
        ultimo_dia = monthrange(ano_int, mes_int)[1]
        data_fim = date(ano_int, mes_int, ultimo_dia)

    # Calcular offset a partir da página
    offset = (page - 1) * page_size

    transactions, total = await service.list_transactions(
        limit=page_size,
        offset=offset,
        tipo=tipo,
        categoria=categoria,
        local_id=local_id,
        painel_id=painel_id,
        descricao=descricao,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    return present_transaction_list(transactions, total, page_size, offset)


@router.get("/transactions/{id}", response_model=TransactionDetailResponse)
async def get_transaction(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca uma transação por ID

    - **id**: ID da transação
    """
    repository = TransactionRepository(session)
    service = TransactionService(repository)
    transaction = await service.get_transaction(id)

    return present_transaction_detail(transaction)


@router.put("/transactions/{id}", response_model=TransactionUpdateResponse)
async def update_transaction(
    id: int,
    request: TransactionUpdateRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza uma transação existente

    - **id**: ID da transação a atualizar
    - Campos no body: mesmos da criação (todos opcionais)
    """
    repository = TransactionRepository(session)
    service = TransactionService(repository)

    # Buscar transação atual
    current = await service.get_transaction(id)

    # Aplicar updates (manter valores atuais se não fornecidos)
    updated_transaction = Transaction(
        id=current.id,
        data=request.data if request.data else current.data,
        descricao=request.descricao if request.descricao else current.descricao,
        valor=request.valor if request.valor else current.valor,
        tipo=TransactionType(request.tipo) if request.tipo else current.tipo,
        categoria=request.categoria if request.categoria else current.categoria,
        recorrencia=Recurrence(request.recorrencia) if request.recorrencia else current.recorrencia,
        parcelas=request.parcelas if request.parcelas is not None else current.parcelas,
        tipo_divisao=TipoDivisao(request.tipo_divisao) if request.tipo_divisao else current.tipo_divisao,
        valor_por_pessoa=request.valor_por_pessoa if request.valor_por_pessoa is not None else current.valor_por_pessoa,
        porcentagem_divisao=request.porcentagem_divisao if request.porcentagem_divisao is not None else current.porcentagem_divisao,
        local_id=request.local_id if request.local_id is not None else current.local_id,
        painel_id=request.painel_id if request.painel_id is not None else current.painel_id,
        # Manter campos de parcelamento e recorrência
        parcela_numero=current.parcela_numero,
        transacao_mae_id=current.transacao_mae_id,
        eh_parcela=current.eh_parcela,
        transacao_recorrente_origem_id=current.transacao_recorrente_origem_id,
        recorrencia_ativa=current.recorrencia_ativa,
        proxima_geracao=current.proxima_geracao,
        criado_em=current.criado_em,
        atualizado_em=current.atualizado_em
    )

    updated = await service.update_transaction(id, updated_transaction)

    return present_transaction_updated(updated)


@router.get("/transactions/{id}/parcelas")
async def list_installments(
    id: int,
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Lista todas as parcelas de uma transação parcelada

    **Requer autenticação** (header X-User-ID em dev)

    Se a transação não for parcelada, retorna apenas ela mesma.
    Se for parcelada, retorna todas as parcelas ordenadas por número.

    - **id**: ID de qualquer parcela da transação
    """
    from src.domain.exceptions import TransactionNotFoundException

    repository = TransactionRepository(session)
    service = TransactionService(repository)

    try:
        # Listar todas as parcelas
        parcelas = await service.list_installments(id)

        # Formatar resposta
        parcelas_data = []
        for parcela in parcelas:
            parcelas_data.append({
                "id": parcela.id,
                "data": parcela.data.isoformat(),
                "descricao": parcela.descricao,
                "valor": float(parcela.valor),
                "tipo": parcela.tipo.value,
                "categoria": parcela.categoria,
                "painel_id": parcela.painel_id,
                "parcelas": parcela.parcelas,
                "parcela_numero": parcela.parcela_numero,
                "eh_parcela": parcela.eh_parcela,
                "transacao_mae_id": parcela.transacao_mae_id
            })

        return {
            "code": "INSTALLMENTS_LIST_SUCCESS",
            "message": f"Encontradas {len(parcelas)} parcela(s)",
            "data": {
                "total": len(parcelas),
                "parcelas": parcelas_data
            }
        }

    except TransactionNotFoundException:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TRANSACTION_NOT_FOUND",
                "message": "Transação não encontrada"
            }
        )


@router.patch("/transactions/{id}/mover")
async def move_transaction(
    id: int,
    painel_id: int = Query(..., description="ID do painel de destino"),
    session: AsyncSession = Depends(get_session),
    usuario_id: int = Depends(get_current_user_id)
):
    """
    Move uma transação para outro painel/cartão

    **Requer autenticação** (header X-User-ID em dev)

    Este é um endpoint especializado para mover transações entre painéis.
    É mais simples que o PUT completo pois requer apenas o painel de destino.

    - **id**: ID da transação a mover
    - **painel_id**: ID do painel/cartão de destino (query parameter)
    """
    from src.domain.exceptions import TransactionNotFoundException

    repository = TransactionRepository(session)
    service = TransactionService(repository)

    try:
        # Buscar transação atual
        current = await service.get_transaction(id)

        # Criar transação atualizada com novo painel
        updated_transaction = Transaction(
            id=current.id,
            data=current.data,
            descricao=current.descricao,
            valor=current.valor,
            tipo=current.tipo,
            categoria=current.categoria,
            recorrencia=current.recorrencia,
            parcelas=current.parcelas,
            tipo_divisao=current.tipo_divisao,
            valor_por_pessoa=current.valor_por_pessoa,
            porcentagem_divisao=current.porcentagem_divisao,
            local_id=current.local_id,
            painel_id=painel_id,  # Novo painel
            # Manter campos de parcelamento e recorrência
            parcela_numero=current.parcela_numero,
            transacao_mae_id=current.transacao_mae_id,
            eh_parcela=current.eh_parcela,
            transacao_recorrente_origem_id=current.transacao_recorrente_origem_id,
            recorrencia_ativa=current.recorrencia_ativa,
            proxima_geracao=current.proxima_geracao,
            criado_em=current.criado_em,
            atualizado_em=current.atualizado_em
        )

        # Atualizar transação
        updated = await service.update_transaction(id, updated_transaction)

        return {
            "code": "TRANSACTION_MOVED",
            "message": f"Transação movida para o painel {painel_id} com sucesso",
            "data": {
                "id": updated.id,
                "data": updated.data.isoformat(),
                "descricao": updated.descricao,
                "valor": float(updated.valor),
                "tipo": updated.tipo.value,
                "categoria": updated.categoria,
                "painel_id": updated.painel_id,
                "painel_anterior": current.painel_id
            }
        }

    except TransactionNotFoundException:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail={
                "code": "TRANSACTION_NOT_FOUND",
                "message": "Transação não encontrada"
            }
        )


@router.delete("/transactions/{id}", status_code=status.HTTP_200_OK, response_model=TransactionDeleteResponse)
async def delete_transaction(
    id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove uma transação

    - **id**: ID da transação a remover
    """
    repository = TransactionRepository(session)
    service = TransactionService(repository)
    await service.delete_transaction(id)

    return present_transaction_deleted()
