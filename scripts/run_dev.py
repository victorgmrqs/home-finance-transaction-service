#!/usr/bin/env python3
"""
Script para executar o projeto em modo de desenvolvimento
"""

import os
import uvicorn
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações padrão para desenvolvimento
os.environ.setdefault("APP_NAME", "Home Finance Transaction Service")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("RELOAD", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./home_finance.db")
os.environ.setdefault("DATABASE_ECHO", "true")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
os.environ.setdefault("SECRET_KEY", "dev-secret-key-that-should-be-at-least-32-characters-long-for-security-reasons-12345")

if __name__ == "__main__":
    print("🚀 Iniciando Home Finance Transaction Service...")
    print("📍 Ambiente: Desenvolvimento")
    print("🌐 Servidor: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/api/v1/health")
    print("-" * 50)
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
