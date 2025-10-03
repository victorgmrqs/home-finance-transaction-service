"""
Aplicação principal do Home Finance Transaction Service
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.adapters.controllers.healthcheck_controller import router as healthcheck_router

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    logger.info(f"Aplicando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")
    
    # Startup
    logger.info("Inicialização da aplicação...")
    try:
        # Aqui você pode adicionar inicializações como:
        # - Conexão com banco de dados
        # - Carregamento de configurações externas
        # - Inicialização de serviços
        pass
    except Exception as e:
        logger.error(f"Erro durante inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Finalização da aplicação...")


# Criação da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Serviço de transações financeiras para controle pessoal",
    debug=settings.debug,
    lifespan=lifespan
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

# Inclusão dos routers
app.include_router(healthcheck_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Rota raiz da aplicação"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}!",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }


@app.get("/info")
async def info():
    """Informações detalhadas da aplicação"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_url": settings.database_url.split("://")[0] + "://[HIDDEN]",  # Ocultar senhas
        "log_level": settings.log_level,
        "cors_origins": settings.cors_origins_list
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
