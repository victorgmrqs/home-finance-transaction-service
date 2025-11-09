"""
Testes de Domínio: Painel
Testa as regras de negócio e validações da entidade Painel
"""

from datetime import datetime

import pytest

from src.domain.models.painel import Painel


class TestPainel:
    """Testes para a entidade Painel"""

    def test_criar_painel_valido(self):
        """Testa criação de painel com dados válidos"""
        painel = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="Gastos da casa"
        )

        assert painel.id == 1
        assert painel.nome == "Casa"
        assert painel.usuario_id == 1
        assert painel.descricao == "Gastos da casa"
        assert painel.criado_em is None
        assert painel.atualizado_em is None

    def test_criar_painel_sem_descricao(self):
        """Testa criação de painel sem descrição"""
        painel = Painel(
            id=1,
            nome="Casa",
            usuario_id=1
        )

        assert painel.id == 1
        assert painel.nome == "Casa"
        assert painel.usuario_id == 1
        assert painel.descricao is None

    def test_criar_painel_nome_vazio(self):
        """Testa erro ao criar painel com nome vazio"""
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Painel(
                id=1,
                nome="",
                usuario_id=1
            )

    def test_criar_painel_nome_apenas_espacos(self):
        """Testa erro ao criar painel com nome apenas espaços"""
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Painel(
                id=1,
                nome="   ",
                usuario_id=1
            )

    def test_criar_painel_nome_muito_longo(self):
        """Testa erro ao criar painel com nome muito longo"""
        nome_longo = "a" * 256
        with pytest.raises(ValueError, match="Nome não pode ter mais de 255 caracteres"):
            Painel(
                id=1,
                nome=nome_longo,
                usuario_id=1
            )

    def test_criar_painel_descricao_muito_longa(self):
        """Testa erro ao criar painel com descrição muito longa"""
        descricao_longa = "a" * 1001
        with pytest.raises(ValueError, match="Descrição não pode ter mais de 1000 caracteres"):
            Painel(
                id=1,
                nome="Casa",
                usuario_id=1,
                descricao=descricao_longa
            )

    def test_criar_painel_usuario_id_nulo(self):
        """Testa erro ao criar painel com usuario_id nulo"""
        with pytest.raises(ValueError, match="ID do usuário é obrigatório e deve ser maior que zero"):
            Painel(
                id=1,
                nome="Casa",
                usuario_id=None
            )

    def test_criar_painel_usuario_id_zero(self):
        """Testa erro ao criar painel com usuario_id zero"""
        with pytest.raises(ValueError, match="ID do usuário é obrigatório e deve ser maior que zero"):
            Painel(
                id=1,
                nome="Casa",
                usuario_id=0
            )

    def test_criar_painel_usuario_id_negativo(self):
        """Testa erro ao criar painel com usuario_id negativo"""
        with pytest.raises(ValueError, match="ID do usuário é obrigatório e deve ser maior que zero"):
            Painel(
                id=1,
                nome="Casa",
                usuario_id=-1
            )

    def test_tem_descricao(self):
        """Testa método tem_descricao"""
        # Painel com descrição
        painel_com_descricao = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="Gastos da casa"
        )
        assert painel_com_descricao.tem_descricao() is True

        # Painel sem descrição
        painel_sem_descricao = Painel(
            id=1,
            nome="Casa",
            usuario_id=1
        )
        assert painel_sem_descricao.tem_descricao() is False

        # Painel com descrição vazia
        painel_descricao_vazia = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao=""
        )
        assert painel_descricao_vazia.tem_descricao() is False

        # Painel com descrição apenas espaços
        painel_descricao_espacos = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="   "
        )
        assert painel_descricao_espacos.tem_descricao() is False

    def test_str_representation(self):
        """Testa representação string do painel"""
        painel = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="Gastos da casa"
        )
        assert str(painel) == "Casa (Usuário: 1)"

    def test_painel_com_timestamps(self):
        """Testa painel com timestamps"""
        agora = datetime.now()
        painel = Painel(
            id=1,
            nome="Casa",
            usuario_id=1,
            descricao="Gastos da casa",
            criado_em=agora,
            atualizado_em=agora
        )

        assert painel.criado_em == agora
        assert painel.atualizado_em == agora

    def test_painel_nomes_validos(self):
        """Testa criação de painéis com nomes válidos"""
        nomes_validos = [
            "Casa",
            "Trabalho",
            "Pessoal",
            "Filhos",
            "Viagem",
            "Casa & Família",
            "Investimentos",
            "Painel 123",
            "Painel-Teste",
            "Painel_Teste"
        ]

        for nome in nomes_validos:
            painel = Painel(
                id=1,
                nome=nome,
                usuario_id=1
            )
            assert painel.nome == nome

    def test_painel_descricoes_validas(self):
        """Testa criação de painéis com descrições válidas"""
        descricoes_validas = [
            "Gastos da casa",
            "Despesas pessoais",
            "Investimentos e poupança",
            "Gastos com filhos e educação",
            "Viagens e lazer",
            "Despesas médicas",
            "Compras online",
            "Supermercado e alimentação",
            "Contas e serviços",
            "Outros gastos diversos"
        ]

        for descricao in descricoes_validas:
            painel = Painel(
                id=1,
                nome="Teste",
                usuario_id=1,
                descricao=descricao
            )
            assert painel.descricao == descricao

    def test_painel_usuario_ids_validos(self):
        """Testa criação de painéis com usuario_ids válidos"""
        usuario_ids_validos = [1, 2, 100, 999, 1000]

        for usuario_id in usuario_ids_validos:
            painel = Painel(
                id=1,
                nome="Teste",
                usuario_id=usuario_id
            )
            assert painel.usuario_id == usuario_id

    def test_painel_descricao_exatamente_1000_caracteres(self):
        """Testa criação de painel com descrição exatamente no limite"""
        descricao_limite = "a" * 1000
        painel = Painel(
            id=1,
            nome="Teste",
            usuario_id=1,
            descricao=descricao_limite
        )
        assert painel.descricao == descricao_limite

    def test_painel_nome_exatamente_255_caracteres(self):
        """Testa criação de painel com nome exatamente no limite"""
        nome_limite = "a" * 255
        painel = Painel(
            id=1,
            nome=nome_limite,
            usuario_id=1
        )
        assert painel.nome == nome_limite
