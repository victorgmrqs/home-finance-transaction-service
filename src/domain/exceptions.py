"""
Domain Exceptions
Exceções customizadas para erros de domínio
"""


class DomainException(Exception):
    """Exceção base para erros de domínio"""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(DomainException):
    """Exceção para erros de validação de dados"""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR")


class TransactionNotFoundException(DomainException):
    """Exceção quando transação não é encontrada"""
    def __init__(self, transaction_id: int):
        message = f"Transação com ID {transaction_id} não encontrada"
        super().__init__(message, code="TRANSACTION_NOT_FOUND")
        self.transaction_id = transaction_id


class LocalNotFoundException(DomainException):
    """Exceção quando local não é encontrado"""
    def __init__(self, local_id: int):
        message = f"Local com ID {local_id} não encontrado"
        super().__init__(message, code="LOCAL_NOT_FOUND")
        self.local_id = local_id


class InvalidTransactionException(DomainException):
    """Exceção para transações inválidas"""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_TRANSACTION")


class InvalidLocalException(DomainException):
    """Exceção para locais inválidos"""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_LOCAL")


class UsuarioNotFoundException(DomainException):
    """Exceção quando usuário não é encontrado"""
    def __init__(self, usuario_id: int = None, email: str = None):
        if usuario_id:
            message = f"Usuário com ID {usuario_id} não encontrado"
        elif email:
            message = f"Usuário com email {email} não encontrado"
        else:
            message = "Usuário não encontrado"
        super().__init__(message, code="USUARIO_NOT_FOUND")
        self.usuario_id = usuario_id
        self.email = email


class InvalidUsuarioException(DomainException):
    """Exceção para usuários inválidos"""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_USUARIO")


class PainelNotFoundException(DomainException):
    """Exceção quando painel não é encontrado"""
    def __init__(self, painel_id: int = None, usuario_id: int = None, nome: str = None):
        if painel_id:
            message = f"Painel com ID {painel_id} não encontrado"
        elif usuario_id and nome:
            message = f"Painel '{nome}' não encontrado para o usuário {usuario_id}"
        else:
            message = "Painel não encontrado"
        super().__init__(message, code="PAINEL_NOT_FOUND")
        self.painel_id = painel_id
        self.usuario_id = usuario_id
        self.nome = nome


class InvalidPainelException(DomainException):
    """Exceção para painéis inválidos"""
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_PAINEL")


class DatabaseException(Exception):
    """Exceção para erros de banco de dados"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class DuplicateCNPJException(DomainException):
    """Exceção quando CNPJ já está cadastrado"""
    def __init__(self, cnpj: str):
        message = f"CNPJ {cnpj} já está cadastrado no sistema"
        super().__init__(message, code="DUPLICATE_CNPJ")
        self.cnpj = cnpj


class DuplicatePainelException(DomainException):
    """Exceção quando painel com mesmo nome já existe para o usuário"""
    def __init__(self, nome: str, usuario_id: int):
        message = f"Painel '{nome}' já existe para o usuário {usuario_id}"
        super().__init__(message, code="DUPLICATE_PAINEL")
        self.nome = nome
        self.usuario_id = usuario_id


class BusinessRuleViolationError(DomainException):
    """Exceção para violação de regras de negócio"""
    def __init__(self, message: str):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION")


class DuplicateEntityError(DomainException):
    """Exceção quando entidade duplicada (ex: email já cadastrado)"""
    def __init__(self, message: str):
        super().__init__(message, code="DUPLICATE_ENTITY")


class EntityNotFoundError(DomainException):
    """Exceção quando entidade não é encontrada"""
    def __init__(self, message: str):
        super().__init__(message, code="ENTITY_NOT_FOUND")
