"""
Aplicação principal do Home Finance Transaction Service
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.adapters.controllers.healthcheck_controller import router as healthcheck_router
from src.adapters.controllers.exception_handlers import register_exception_handlers
from src.adapters.middlewares.auth_middleware import MockAuthMiddleware

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

# Middleware de autenticação mock
app.add_middleware(MockAuthMiddleware, environment=settings.environment)

# Registrar exception handlers
register_exception_handlers(app)

# Inclusão dos routers
app.include_router(healthcheck_router, prefix="", tags=["Health"])

# Importar e registrar routers de negócio
from src.adapters.controllers.transaction_controller import router as transaction_router
from src.adapters.controllers.local_controller import router as local_router
from src.adapters.controllers.usuario_controller import router as usuario_router
from src.adapters.controllers.painel_controller import router as painel_router
from src.adapters.controllers.painel_sharing_controller import router as painel_sharing_router
from src.adapters.controllers.painel_analytics_controller import router as painel_analytics_router

# Business routers (versionamento /api/v1)
app.include_router(transaction_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(local_router, prefix="/api/v1", tags=["Locais"])
app.include_router(usuario_router, prefix="/api/v1", tags=["Usuários"])
app.include_router(painel_router, prefix="/api/v1", tags=["Painéis"])
app.include_router(painel_sharing_router, prefix="/api/v1", tags=["Painéis - Compartilhamento"])
app.include_router(painel_analytics_router, prefix="/api/v1", tags=["Painéis - Analytics"])




if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
