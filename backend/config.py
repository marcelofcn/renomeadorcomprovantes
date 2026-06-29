"""
Configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Renomeador de Comprovantes"
    APP_VERSION: str = "2.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # JWT
    SECRET_KEY: str = "sua-chave-secreta-64-caracteres-min-em-producao-mude-isso"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    
    # API
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar variáveis extras no .env


settings = Settings()

# CORS Origins (hardcoded, pode ser ajustado por environment variable se necessário)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
]

