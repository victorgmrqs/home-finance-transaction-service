"""
Entidade de Domínio: Local
Representa um local onde transações podem ocorrer (lojas, mercados, etc.)
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Local:
    """
    Entidade de domínio: Local

    Representa um estabelecimento/local onde transações financeiras ocorrem.
    Conforme ADR-002, permite registro incremental de informações.
    """
    id: int | None
    nome_fantasia: str | None = None
    cnpj: str | None = None
    razao_social: str | None = None
    categoria: str | None = None
    endereco: str | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None

    def __post_init__(self):
        """Valida o local após inicialização"""
        self._validate()

    def _validate(self):
        """Valida regras de negócio do local"""
        if not self.nome_fantasia and not self.cnpj:
            raise ValueError("Local deve ter pelo menos nome fantasia ou CNPJ")

        if self.cnpj and not self._validar_cnpj(self.cnpj):
            raise ValueError("CNPJ inválido")

        if self.nome_fantasia and len(self.nome_fantasia) > 255:
            raise ValueError("Nome fantasia não pode ter mais de 255 caracteres")

        if self.razao_social and len(self.razao_social) > 255:
            raise ValueError("Razão social não pode ter mais de 255 caracteres")

        if self.categoria and len(self.categoria) > 100:
            raise ValueError("Categoria não pode ter mais de 100 caracteres")

    def _validar_cnpj(self, cnpj: str) -> bool:
        """
        Valida formato básico do CNPJ

        Aceita CNPJ com ou sem formatação.
        Validação completa de dígitos verificadores pode ser implementada futuramente.
        """
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

        # CNPJ deve ter exatamente 14 dígitos
        if len(cnpj_limpo) != 14:
            return False

        # Verifica se não é sequência de dígitos repetidos
        if cnpj_limpo == cnpj_limpo[0] * 14:
            return False

        return True

    def is_completo(self) -> bool:
        """Verifica se o local tem dados completos (ADR-002)"""
        return all([
            self.nome_fantasia,
            self.cnpj,
            self.razao_social
        ])

    def is_rascunho(self) -> bool:
        """Verifica se o local é um rascunho (dados incompletos)"""
        return not self.is_completo()

    def formatar_cnpj(self) -> str | None:
        """Retorna CNPJ formatado (XX.XXX.XXX/XXXX-XX)"""
        if not self.cnpj:
            return None

        cnpj_limpo = ''.join(filter(str.isdigit, self.cnpj))

        if len(cnpj_limpo) != 14:
            return self.cnpj

        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    def __str__(self) -> str:
        return self.nome_fantasia or self.razao_social or f"CNPJ: {self.cnpj}" or "Local sem identificação"
