from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Voice Agent"
    
    # Retell AI
    RETELL_API_KEY: str
    RETELL_BASE_URL: str = "https://api.retellai.com"
    RETELL_LLM_ID:str=""
    RETELL_FROM_NUMBER: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Google Gemini for post-processing
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Security
    WEBHOOK_SECRET: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


