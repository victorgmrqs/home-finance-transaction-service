"""
Configurações da aplicação home-finance-transaction-service
Baseado em Pydantic Settings para validação e type hints
"""

import os
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações principais da aplicação"""

    # Informações básicas da aplicação
    app_name: str = Field(default="Home Finance Transaction Service", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Configurações do servidor
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")

    # Configurações do banco de dados
    database_url: str = Field(env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Configurações de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")

    # Configurações de CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080", env="CORS_ORIGINS")
    cors_methods: str = Field(default="GET,POST,PUT,DELETE", env="CORS_METHODS")
    cors_headers: str = Field(default="*", env="CORS_HEADERS")

    # Configurações de segurança
    secret_key: str = Field(env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")

    # Configurações de rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Configurações externas (ex: APIs de terceiros)
    external_api_timeout: int = Field(default=30, env="EXTERNAL_API_TIMEOUT")
    external_api_retries: int = Field(default=3, env="EXTERNAL_API_RETRIES")

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

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8"
    }


class DevelopmentConfig(Settings):
    """Configurações específicas para desenvolvimento"""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    database_echo: bool = True

    model_config = {
        "env_prefix": "DEV_",
        **Settings.model_config
    }


class StagingConfig(Settings):
    """Configurações específicas para staging"""
    debug: bool = False
    reload: bool = False
    log_level: str = "INFO"

    model_config = {
        "env_prefix": "STAGING_",
        **Settings.model_config
    }


class ProductionConfig(Settings):
    """Configurações específicas para produção"""
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"

    model_config = {
        "env_prefix": "PROD_",
        **Settings.model_config
    }


class TestingConfig(Settings):
    """Configurações específicas para testes"""
    debug: bool = False
    reload: bool = False
    log_level: str = "DEBUG"
    database_url: str = "sqlite+aiosqlite:///./test.db"

    model_config = {
        "env_prefix": "TEST_U",
        **Settings.model_config
    }


@lru_cache
def get_settings() -> Settings:
    """
    Factory function para obter as configurações baseadas no ambiente

    Isso garante que as configurações sejam carregadas apenas uma vez
    e sejam consistentes durante toda a execução da aplicação
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    config_classes = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_classes.get(environment, Settings)
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
