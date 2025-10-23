"""
Testes unitários para validação de divisão de gastos em Transações
"""

import pytest
from decimal import Decimal
from datetime import date
from src.domain.models.transaction import Transaction, TransactionType, TipoDivisao


def test_transaction_gasto_pessoal():
    """Testa criação de transação com gasto pessoal (padrão)"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Mercado",
        valor=Decimal("200.00"),
        tipo=TransactionType.SAIDA,
        categoria="Alimentação",
        painel_id=1
    )
    assert transaction.tipo_divisao == TipoDivisao.PESSOAL
    assert transaction.is_gasto_pessoal()
    assert not transaction.is_gasto_compartilhado()


def test_transaction_gasto_compartilhado_50_50():
    """Testa criação de transação com divisão 50/50"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Jantar Restaurante",
        valor=Decimal("100.00"),
        tipo=TransactionType.SAIDA,
        categoria="Alimentação",
        painel_id=1,
        tipo_divisao=TipoDivisao.COMPARTILHADO_50_50,
        valor_por_pessoa=Decimal("50.00")
    )
    assert transaction.tipo_divisao == TipoDivisao.COMPARTILHADO_50_50
    assert transaction.valor_por_pessoa == Decimal("50.00")
    assert transaction.is_gasto_compartilhado()
    assert not transaction.is_gasto_pessoal()


def test_transaction_gasto_compartilhado_custom():
    """Testa criação de transação com divisão customizada"""
    transaction = Transaction(
        id=None,
        data=date(2025, 1, 15),
        descricao="Aluguel",
        valor=Decimal("1000.00"),
        tipo=TransactionType.SAIDA,
        categoria="Moradia",
        painel_id=1,
        tipo_divisao=TipoDivisao.COMPARTILHADO_CUSTOM,
        valor_por_pessoa=Decimal("600.00"),
        porcentagem_divisao=60
    )
    assert transaction.tipo_divisao == TipoDivisao.COMPARTILHADO_CUSTOM
    assert transaction.valor_por_pessoa == Decimal("600.00")
    assert transaction.porcentagem_divisao == 60
    assert transaction.is_gasto_compartilhado()


def test_transaction_compartilhado_custom_sem_porcentagem():
    """Testa que divisão customizada sem porcentagem gera erro"""
    with pytest.raises(ValueError, match="porcentagem_divisao é obrigatória"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            tipo=TransactionType.SAIDA,
            categoria="Moradia",
            painel_id=1,
            tipo_divisao=TipoDivisao.COMPARTILHADO_CUSTOM,
            valor_por_pessoa=Decimal("600.00")
        )


def test_transaction_porcentagem_divisao_invalida():
    """Testa que porcentagem fora do range 1-100 gera erro"""
    with pytest.raises(ValueError, match="porcentagem_divisao deve estar entre 1 e 100"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Aluguel",
            valor=Decimal("1000.00"),
            tipo=TransactionType.SAIDA,
            categoria="Moradia",
            painel_id=1,
            tipo_divisao=TipoDivisao.COMPARTILHADO_CUSTOM,
            valor_por_pessoa=Decimal("1500.00"),
            porcentagem_divisao=150
        )


def test_transaction_valor_por_pessoa_negativo():
    """Testa que valor_por_pessoa negativo gera erro"""
    with pytest.raises(ValueError, match="valor_por_pessoa não pode ser negativo"):
        Transaction(
            id=None,
            data=date(2025, 1, 15),
            descricao="Mercado",
            valor=Decimal("100.00"),
            tipo=TransactionType.SAIDA,
            categoria="Alimentação",
            painel_id=1,
            tipo_divisao=TipoDivisao.COMPARTILHADO_50_50,
            valor_por_pessoa=Decimal("-50.00")
        )


def test_transaction_str_com_divisao():
    """Testa representação em string de transação com divisão"""
    transaction = Transaction(
        id=1,
        data=date(2025, 1, 15),
        descricao="Jantar",
        valor=Decimal("100.00"),
        tipo=TransactionType.SAIDA,
        categoria="Alimentação",
        painel_id=1,
        tipo_divisao=TipoDivisao.COMPARTILHADO_50_50,
        valor_por_pessoa=Decimal("50.00")
    )
    str_representation = str(transaction)
    assert "COMPARTILHADO_50_50" in str_representation
    assert "Jantar" in str_representation
