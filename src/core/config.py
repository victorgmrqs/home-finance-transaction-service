"""
Configurações da aplicação home-finance-transaction-service
Baseado em Pydantic Settings para validação e type hints
"""

import os
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações principais da aplicação"""

    # Informações básicas da aplicação
    app_name: str = "Home Finance Transaction Service"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Configurações do servidor
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Configurações do banco de dados
    database_url: str = ""
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 20

    # Configurações de logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configurações de CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    cors_methods: str = "GET,POST,PUT,DELETE"
    cors_headers: str = "*"

    # Configurações de segurança
    secret_key: str = ""
    access_token_expire_minutes: int = 30
    bcrypt_rounds: int = 12

    # Configurações de cookies
    cookie_name: str = "auth_token"
    cookie_httponly: bool = True
    cookie_secure: bool = False  # True apenas em produção (HTTPS)
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"  # lax, strict ou none
    cookie_max_age: int = 1800  # 30 minutos (em segundos)

    # Configurações de rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Configurações externas (ex: APIs de terceiros)
    external_api_timeout: int = 30
    external_api_retries: int = 3

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        """Valida se a URL do banco está configurada"""
        if not v:
            raise ValueError("DATABASE_URL é obrigatória")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Valida se a secret key está configurada"""
        if not v:
            raise ValueError("SECRET_KEY é obrigatória")
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres")
        return v


    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Valida se o ambiente está dentro dos valores permitidos"""
        allowed_envs = ["development", "staging", "production", "testing"]
        if v not in allowed_envs:
            raise ValueError(f"Ambiente deve ser um dos: {allowed_envs}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Valida se o nível de log está dentro dos valores permitidos"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Nível de log deve ser um dos: {allowed_levels}")
        return v.upper()

    @field_validator("cookie_samesite", mode="before")
    @classmethod
    def validate_cookie_samesite(cls, v):
        """Valida se o valor de SameSite está dentro dos valores permitidos"""
        if isinstance(v, str):
            v_lower = v.lower()
            allowed_values = ["lax", "strict", "none"]
            if v_lower not in allowed_values:
                raise ValueError(f"cookie_samesite deve ser um dos: {allowed_values}")
            return v_lower
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origins do CORS"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> list[str]:
        """Retorna lista de métodos do CORS"""
        return [method.strip() for method in self.cors_methods.split(",")]

    @property
    def cors_headers_list(self) -> list[str]:
        """Retorna lista de headers do CORS"""
        return [header.strip() for header in self.cors_headers.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )


class DevelopmentConfig(Settings):
    """Configurações específicas para desenvolvimento"""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    database_echo: bool = True
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    secret_key: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        env_prefix="DEV_",
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )


class StagingConfig(Settings):
    """Configurações específicas para staging"""
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"
    database_url: str = ""
    secret_key: str = ""

    model_config = SettingsConfigDict(
        env_prefix="STAGING_",
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )


class ProductionConfig(Settings):
    """Configurações específicas para produção"""
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    database_url: str = ""
    secret_key: str = ""
    cookie_secure: bool = True  # HTTPS obrigatório em produção

    model_config = SettingsConfigDict(
        env_prefix="PROD_",
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )


class TestingConfig(Settings):
    """Configurações específicas para testes"""
    debug: bool = False
    reload: bool = False
    log_level: str = "DEBUG"
    database_url: str = "sqlite+aiosqlite:///./test.db"

    model_config = SettingsConfigDict(
        env_prefix="TEST_U",
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Factory function para obter as configurações baseadas no ambiente

    Isso garante que as configurações sejam carregadas apenas uma vez
    e sejam consistentes durante toda a execução da aplicação
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    config_classes: dict[str, type[Settings]] = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_classes.get(environment, Settings)
    if config_class == Settings:
        # Para Settings base, precisamos passar os campos obrigatórios
        # Em produção, esses valores devem vir de variáveis de ambiente
        database_url = os.getenv("DATABASE_URL", "")
        secret_key = os.getenv("SECRET_KEY", "")
        if not database_url or not secret_key:
            # Se não tiver as variáveis, usar valores padrão (válidos apenas para testes)
            database_url = database_url or "sqlite+aiosqlite:///./default.db"
            secret_key = secret_key or "default-secret-key-for-development-only-change-in-production"
        return config_class(
            database_url=database_url,
            secret_key=secret_key
        )
    return config_class()


# Instância global das configurações
settings = get_settings()


# Conveniência para registrar o schema do banco (usado pelo Alembic)
def get_database_url() -> str:
    """Retorna a URL do banco de dados"""
    return settings.database_url


def is_production() -> bool:
    """Verifica se está rodando em produção"""
    return settings.environment == "production"


def is_development() -> bool:
    """Verifica se está rodando em desenvolvimento"""
    return settings.environment == "development"


def is_testing() -> bool:
    """Verifica se está rodando em modo de teste"""
    return settings.environment == "testing"
