"""
Testes de Domínio: Usuario
Testa as regras de negócio e validações da entidade Usuario
"""

import pytest
from datetime import datetime
from src.domain.models.usuario import Usuario


class TestUsuario:
    """Testes para a entidade Usuario"""

    def test_criar_usuario_valido(self):
        """Testa criação de usuário com dados válidos"""
        usuario = Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com"
        )

        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@example.com"
        assert usuario.criado_em is None
        assert usuario.atualizado_em is None

    def test_criar_usuario_sem_email(self):
        """Testa criação de usuário sem email"""
        usuario = Usuario(
            id=1,
            nome="João Silva"
        )

        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email is None

    def test_criar_usuario_nome_vazio(self):
        """Testa erro ao criar usuário com nome vazio"""
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Usuario(
                id=1,
                nome=""
            )

    def test_criar_usuario_nome_apenas_espacos(self):
        """Testa erro ao criar usuário com nome apenas espaços"""
        with pytest.raises(ValueError, match="Nome é obrigatório e não pode ser vazio"):
            Usuario(
                id=1,
                nome="   "
            )

    def test_criar_usuario_nome_muito_longo(self):
        """Testa erro ao criar usuário com nome muito longo"""
        nome_longo = "a" * 256
        with pytest.raises(ValueError, match="Nome não pode ter mais de 255 caracteres"):
            Usuario(
                id=1,
                nome=nome_longo
            )

    def test_criar_usuario_email_muito_longo(self):
        """Testa erro ao criar usuário com email muito longo"""
        email_longo = "a" * 250 + "@example.com"
        with pytest.raises(ValueError, match="Email não pode ter mais de 255 caracteres"):
            Usuario(
                id=1,
                nome="João Silva",
                email=email_longo
            )

    def test_criar_usuario_email_invalido_sem_arroba(self):
        """Testa erro ao criar usuário com email sem @"""
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joaoexample.com"
            )

    def test_criar_usuario_email_invalido_sem_dominio(self):
        """Testa erro ao criar usuário com email sem domínio"""
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joao@"
            )

    def test_criar_usuario_email_invalido_sem_ponto(self):
        """Testa erro ao criar usuário com email sem ponto no domínio"""
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joao@example"
            )

    def test_criar_usuario_email_valido(self):
        """Testa criação de usuário com emails válidos"""
        emails_validos = [
            "joao@example.com",
            "maria.silva@empresa.com.br",
            "user123@domain.org",
            "test+tag@example.co.uk"
        ]

        for email in emails_validos:
            usuario = Usuario(
                id=1,
                nome="João Silva",
                email=email
            )
            assert usuario.email == email

    def test_tem_email(self):
        """Testa método tem_email"""
        # Usuário com email
        usuario_com_email = Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com"
        )
        assert usuario_com_email.tem_email() is True

        # Usuário sem email
        usuario_sem_email = Usuario(
            id=1,
            nome="João Silva"
        )
        assert usuario_sem_email.tem_email() is False

        # Usuário com email vazio (não é permitido pelo modelo)
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email=""
            )

        # Usuário com email apenas espaços (não é permitido pelo modelo)
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="   "
            )

    def test_str_representation(self):
        """Testa representação string do usuário"""
        # Usuário com email
        usuario_com_email = Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com"
        )
        assert str(usuario_com_email) == "João Silva (joao@example.com)"

        # Usuário sem email
        usuario_sem_email = Usuario(
            id=1,
            nome="João Silva"
        )
        assert str(usuario_sem_email) == "João Silva (sem email)"

    def test_usuario_com_timestamps(self):
        """Testa usuário com timestamps"""
        agora = datetime.now()
        usuario = Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com",
            criado_em=agora,
            atualizado_em=agora
        )

        assert usuario.criado_em == agora
        assert usuario.atualizado_em == agora

    def test_validacao_email_edge_cases(self):
        """Testa casos extremos de validação de email"""
        # Email com múltiplos @
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joao@@example.com"
            )

        # Email vazio
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email=""
            )

        # Email apenas espaços
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="   "
            )

        # Email sem @
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joaoexample.com"
            )

        # Email sem domínio
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joao@"
            )

        # Email sem ponto no domínio
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(
                id=1,
                nome="João Silva",
                email="joao@example"
            )
