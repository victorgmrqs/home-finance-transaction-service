"""
Transaction Presenter
Formatação de responses para endpoints de transações
"""


from src.domain.models.transaction import Transaction
from src.shared.responses import success_response


def present_transaction(transaction: Transaction) -> dict:
    """
    Apresenta uma transação como resposta da API

    Args:
        transaction: Entidade de transação

    Returns:
        dict: Response formatado conforme contrato
    """
    return {
        "id": transaction.id,
        "data": transaction.data.isoformat(),
        "descricao": transaction.descricao,
        "valor": float(transaction.valor),
        "tipo": transaction.tipo.value,
        "categoria": transaction.categoria,
        "recorrencia": transaction.recorrencia.value if transaction.recorrencia else None,
        "parcelas": transaction.parcelas,
        "tipo_divisao": transaction.tipo_divisao.value if transaction.tipo_divisao else "PESSOAL",
        "valor_por_pessoa": float(transaction.valor_por_pessoa) if transaction.valor_por_pessoa else None,
        "porcentagem_divisao": transaction.porcentagem_divisao,
        "local_id": transaction.local_id,
        "painel_id": transaction.painel_id,
        "criado_em": transaction.criado_em.isoformat() if transaction.criado_em else None,
        "atualizado_em": transaction.atualizado_em.isoformat() if transaction.atualizado_em else None
    }


def present_transaction_created(transaction: Transaction) -> dict:
    """Apresenta resposta de transação criada"""
    return success_response(
        code="TRANSACTION_CREATED",
        message="Transação criada com sucesso",
        data=present_transaction(transaction)
    )


def present_transaction_detail(transaction: Transaction) -> dict:
    """Apresenta resposta de detalhe de transação"""
    return success_response(
        code="TRANSACTION_DETAIL_SUCCESS",
        message="Transação encontrada",
        data=present_transaction(transaction)
    )


def present_transaction_list(
    transactions: list[Transaction],
    total: int,
    limit: int,
    offset: int
) -> dict:
    """
    Apresenta lista de transações com paginação

    Args:
        transactions: Lista de transações
        total: Total de registros
        limit: Limite de resultados
        offset: Offset da paginação

    Returns:
        dict: Response formatado com lista e metadados
    """
    return success_response(
        code="TRANSACTION_LIST_SUCCESS",
        message="Lista de transações obtida com sucesso",
        data=[present_transaction(t) for t in transactions]
    )


def present_transaction_updated(transaction: Transaction) -> dict:
    """Apresenta resposta de transação atualizada"""
    return success_response(
        code="TRANSACTION_UPDATED",
        message="Transação atualizada com sucesso",
        data=present_transaction(transaction)
    )


def present_transaction_deleted() -> dict:
    """Apresenta resposta de transação deletada"""
    return success_response(
        code="TRANSACTION_DELETED",
        message="Transação removida com sucesso",
        data=None
    )
