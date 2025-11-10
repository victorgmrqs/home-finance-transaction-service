"""
Testes unitários para validação de tipo_conta em Painéis
"""

import pytest

from src.domain.models.painel import Painel


def test_painel_com_tipo_conta_cartao_credito():
    """Testa criação de painel com tipo CARTAO_CREDITO"""
    painel = Painel(
        id=None,
        nome="Cartão Nubank",
        tipo_conta="CARTAO_CREDITO",
        usuario_id=1
    )
    assert painel.tipo_conta == "CARTAO_CREDITO"


def test_painel_com_tipo_conta_conta_bancaria():
    """Testa criação de painel com tipo CONTA_BANCARIA"""
    painel = Painel(
        id=None,
        nome="Conta Corrente",
        tipo_conta="CONTA_BANCARIA",
        usuario_id=1
    )
    assert painel.tipo_conta == "CONTA_BANCARIA"


def test_painel_com_tipo_conta_dinheiro():
    """Testa criação de painel com tipo DINHEIRO"""
    painel = Painel(
        id=None,
        nome="Carteira",
        tipo_conta="DINHEIRO",
        usuario_id=1
    )
    assert painel.tipo_conta == "DINHEIRO"


def test_painel_com_tipo_conta_invalido():
    """Testa que tipo_conta inválido gera erro"""
    with pytest.raises(ValueError, match="tipo_conta deve ser um de"):
        Painel(
            id=None,
            nome="Painel Teste",
            tipo_conta="INVALIDO",
            usuario_id=1
        )


def test_painel_com_tipo_conta_default():
    """Testa que tipo_conta padrão é CARTAO_CREDITO"""
    painel = Painel(
        id=None,
        nome="Painel Padrão",
        usuario_id=1
    )
    assert painel.tipo_conta == "CARTAO_CREDITO"
