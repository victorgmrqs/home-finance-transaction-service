"""
Testes para a entidade de domínio Transaction
"""

import pytest
from decimal import Decimal
from datetime import date
from src.domain.models.transaction import Transaction, TransactionType, Recurrence


def test_criar_transacao_valida():
    """Testa criação de transação válida"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Salário",
        valor=Decimal("5000.00"),
        tipo=TransactionType.ENTRADA,
        categoria="salario",
        painel_id=1
    )

    assert transaction.descricao == "Salário"
    assert transaction.valor == Decimal("5000.00")
    assert transaction.tipo == TransactionType.ENTRADA
    assert transaction.painel_id == 1
    assert not transaction.is_parcelada()
    assert transaction.is_entrada()
    assert not transaction.is_saida()


def test_transacao_com_valor_negativo_deve_falhar():
    """Testa que valor negativo lança exceção"""
    with pytest.raises(ValueError, match="Valor deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("-100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=1
        )


def test_transacao_com_valor_zero_deve_falhar():
    """Testa que valor zero lança exceção"""
    with pytest.raises(ValueError, match="Valor deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("0.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=1
        )


def test_transacao_sem_descricao_deve_falhar():
    """Testa que descrição vazia lança exceção"""
    with pytest.raises(ValueError, match="Descrição é obrigatória"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=1
        )


def test_transacao_sem_categoria_deve_falhar():
    """Testa que categoria vazia lança exceção"""
    with pytest.raises(ValueError, match="Categoria é obrigatória"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="",
            painel_id=1
        )


def test_transacao_parcelada():
    """Testa transação parcelada"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Notebook",
        valor=Decimal("3000.00"),
        tipo=TransactionType.SAIDA,
        categoria="tecnologia",
        painel_id=1,
        parcelas=10
    )

    assert transaction.is_parcelada()
    assert transaction.valor_parcela() == Decimal("300.00")


def test_transacao_recorrente():
    """Testa transação recorrente"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Aluguel",
        valor=Decimal("1500.00"),
        tipo=TransactionType.SAIDA,
        categoria="moradia",
        painel_id=1,
        recorrencia=Recurrence.MENSAL
    )

    assert transaction.is_recorrente()


def test_transacao_ocasional_nao_e_recorrente():
    """Testa que transação ocasional não é considerada recorrente"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Presente",
        valor=Decimal("50.00"),
        tipo=TransactionType.SAIDA,
        categoria="presentes",
        painel_id=1,
        recorrencia=Recurrence.OCASIONAL
    )

    assert not transaction.is_recorrente()


def test_transacao_com_parcelas_invalidas_deve_falhar():
    """Testa que parcelas inválidas lançam exceção"""
    with pytest.raises(ValueError, match="Número de parcelas deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=1,
            parcelas=0
        )


def test_transacao_sem_painel_id_deve_falhar():
    """Testa que painel_id nulo lança exceção"""
    with pytest.raises(ValueError, match="ID do painel é obrigatório e deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=None
        )


def test_transacao_com_painel_id_zero_deve_falhar():
    """Testa que painel_id zero lança exceção"""
    with pytest.raises(ValueError, match="ID do painel é obrigatório e deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=0
        )


def test_transacao_com_painel_id_negativo_deve_falhar():
    """Testa que painel_id negativo lança exceção"""
    with pytest.raises(ValueError, match="ID do painel é obrigatório e deve ser maior que zero"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Compra",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="compras",
            painel_id=-1
        )


def test_transacao_com_painel_id_valido():
    """Testa criação de transação com painel_id válido"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Compra",
        valor=Decimal("100.00"),
        tipo=TransactionType.SAIDA,
        categoria="compras",
        painel_id=5
    )

    assert transaction.painel_id == 5


def test_transacao_com_local_id_opcional():
    """Testa criação de transação com local_id opcional"""
    # Com local_id
    transaction_com_local = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Compra",
        valor=Decimal("100.00"),
        tipo=TransactionType.SAIDA,
        categoria="compras",
        painel_id=1,
        local_id=3
    )
    assert transaction_com_local.local_id == 3

    # Sem local_id
    transaction_sem_local = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Compra",
        valor=Decimal("100.00"),
        tipo=TransactionType.SAIDA,
        categoria="compras",
        painel_id=1
    )
    assert transaction_sem_local.local_id is None


def test_transacao_com_todos_campos():
    """Testa criação de transação com todos os campos"""
    transaction = Transaction(
        id=1,
        data=date(2025, 1, 15),
        descricao="Notebook parcelado",
        valor=Decimal("3000.00"),
        tipo=TransactionType.SAIDA,
        categoria="tecnologia",
        painel_id=2,
        recorrencia=Recurrence.OCASIONAL,
        parcelas=12,
        local_id=5
    )

    assert transaction.id == 1
    assert transaction.data == date(2025, 1, 15)
    assert transaction.descricao == "Notebook parcelado"
    assert transaction.valor == Decimal("3000.00")
    assert transaction.tipo == TransactionType.SAIDA
    assert transaction.categoria == "tecnologia"
    assert transaction.painel_id == 2
    assert transaction.recorrencia == Recurrence.OCASIONAL
    assert transaction.parcelas == 12
    assert transaction.local_id == 5
    assert transaction.is_parcelada()
    assert transaction.valor_parcela() == Decimal("250.00")
    assert not transaction.is_recorrente()
    assert transaction.is_saida()
    assert not transaction.is_entrada()
