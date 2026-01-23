from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/myappstore"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Google Custom Search
    GOOGLE_CUSTOM_SEARCH_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""

    # SMTP Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "MyApp Store"
    APP_URL: str = "http://localhost:5900"  # Frontend URL for invitation links

    # Paths - 환경변수로 관리
    SCAN_BASE_PATH: str = "/library"
    ICON_CACHE_DIR: str = "/home/nuricom/project/myappStore/data/icons"
    SCREENSHOT_CACHE_DIR: str = "/home/nuricom/project/myappStore/data/screenshots"
    EXIMAGE_DIR: str = "/home/nuricom/project/myappStore/data/eximage"
    PATCHES_DIR: str = "/home/nuricom/project/myappStore/data/patches"
    CONFIG_DATA_DIR: str = "/home/nuricom/project/myappStore/data"
    SCAN_EXCLUSIONS_FILE: str = "/home/nuricom/project/myappStore/data/scan_exclusions.txt"

    # CORS - comma-separated string
    CORS_ORIGINS: str = "http://localhost:5900,http://localhost:3000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8110
    BACKEND_URL: str = "http://localhost:8110"  # Backend URL for image paths

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: str = "/home/nuricom/project/myappStore/data/logs"
    ENVIRONMENT: str = "development"  # development, production

    class Config:
        env_file = ".env"

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        # If "*" is set, allow all origins
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
