"""
Testes para a entidade de domínio Local
"""

import pytest
from src.domain.models.local import Local


def test_criar_local_valido_com_nome_fantasia():
    """Testa criação de local válido apenas com nome fantasia"""
    local = Local(
        id=None,
        nome_fantasia="Padaria do João"
    )

    assert local.nome_fantasia == "Padaria do João"
    assert local.is_rascunho()
    assert not local.is_completo()


def test_criar_local_valido_com_cnpj():
    """Testa criação de local válido apenas com CNPJ"""
    local = Local(
        id=None,
        cnpj="12345678000190"
    )

    assert local.cnpj == "12345678000190"
    assert local.is_rascunho()


def test_criar_local_completo():
    """Testa criação de local com dados completos"""
    local = Local(
        id=None,
        nome_fantasia="Supermercado Exemplo",
        cnpj="12345678000190",
        razao_social="Supermercado Exemplo LTDA"
    )

    assert local.is_completo()
    assert not local.is_rascunho()


def test_local_sem_nome_e_cnpj_deve_falhar():
    """Testa que local sem nome fantasia nem CNPJ lança exceção"""
    with pytest.raises(ValueError, match="Local deve ter pelo menos nome fantasia ou CNPJ"):
        Local(id=None)


def test_local_com_cnpj_invalido_deve_falhar():
    """Testa que CNPJ inválido lança exceção"""
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Local(
            id=None,
            nome_fantasia="Loja Exemplo",
            cnpj="123"  # CNPJ muito curto
        )


def test_cnpj_com_digitos_repetidos_deve_falhar():
    """Testa que CNPJ com todos dígitos iguais é inválido"""
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Local(
            id=None,
            nome_fantasia="Loja Exemplo",
            cnpj="11111111111111"
        )


def test_formatar_cnpj():
    """Testa formatação de CNPJ"""
    local = Local(
        id=None,
        nome_fantasia="Loja",
        cnpj="12345678000190"
    )

    assert local.formatar_cnpj() == "12.345.678/0001-90"


def test_formatar_cnpj_ja_formatado():
    """Testa formatação de CNPJ que já está formatado"""
    local = Local(
        id=None,
        nome_fantasia="Loja",
        cnpj="12.345.678/0001-90"
    )

    assert local.formatar_cnpj() == "12.345.678/0001-90"


def test_local_str_com_nome_fantasia():
    """Testa representação em string com nome fantasia"""
    local = Local(
        id=None,
        nome_fantasia="Padaria do João"
    )

    assert str(local) == "Padaria do João"


def test_local_str_com_cnpj():
    """Testa representação em string apenas com CNPJ"""
    local = Local(
        id=None,
        cnpj="12345678000190"
    )

    assert "CNPJ" in str(local)
