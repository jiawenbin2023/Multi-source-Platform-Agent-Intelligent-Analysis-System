from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    qwen_api_key: Optional[str] = None
    tushare_token: Optional[str] = None

    default_model: str = "qwen-turbo"
    temperature: float = 0.1

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
