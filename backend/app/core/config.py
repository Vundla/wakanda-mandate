from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "mysql+pymysql://vundla:Mv@20217$@localhost:3306/wakanda_db"
    
    # API settings
    api_title: str = "Wakanda Digital Government Platform"
    api_version: str = "1.0.0"
    api_description: str = "Enterprise backend foundation for digital government services"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI settings (OpenRouter)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()