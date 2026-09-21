import os

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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days - stay logged in

    # AI
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""

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
    #
    # 기본값은 DATA_DIR 기준이며, DATA_DIR 자체도 환경변수로 바꿀 수 있다.
    # docker-compose 는 아래 값들을 모두 명시적으로 주입하므로 운영에서는
    # 기본값이 쓰이지 않지만, compose 밖(로컬 uvicorn, 테스트 등)에서는
    # 이 기본값으로 동작한다.
    #
    # 예전에는 "/home/nuricom/project/myappStore/data/..." 처럼 특정 개발 머신의
    # 절대 경로가 기본값이었다. 다른 환경에서는 존재하지 않는 경로다.
    DATA_DIR: str = os.getenv("DATA_DIR", "/app/data")

    SCAN_BASE_PATH: str = os.getenv("SCAN_BASE_PATH", f"{DATA_DIR}/library")
    ICON_CACHE_DIR: str = os.getenv("ICON_CACHE_DIR", f"{DATA_DIR}/icons")
    SCREENSHOT_CACHE_DIR: str = os.getenv("SCREENSHOT_CACHE_DIR", f"{DATA_DIR}/screenshots")
    EXIMAGE_DIR: str = os.getenv("EXIMAGE_DIR", f"{DATA_DIR}/eximage")
    PATCHES_DIR: str = os.getenv("PATCHES_DIR", f"{DATA_DIR}/patches")
    ATTACHMENTS_DIR: str = os.getenv("ATTACHMENTS_DIR", f"{DATA_DIR}/attachments")
    CONFIG_DATA_DIR: str = os.getenv("CONFIG_DATA_DIR", DATA_DIR)
    SCAN_EXCLUSIONS_FILE: str = os.getenv("SCAN_EXCLUSIONS_FILE", f"{DATA_DIR}/scan_exclusions.txt")
    VIDEOS_DIR: str = os.getenv("VIDEOS_DIR", f"{DATA_DIR}/videos")

    # CORS - comma-separated string
    CORS_ORIGINS: str = "http://localhost:5900,http://localhost:3000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8110
    BACKEND_URL: str = ""  # Backend URL for image paths (will be auto-generated if empty)

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_DIR: str = os.getenv("LOG_DIR", f"{DATA_DIR}/logs")
    ENVIRONMENT: str = "development"  # development, production

    class Config:
        env_file = ".env"

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        # If "*" is set, allow all origins
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def get_backend_url(self) -> str:
        """Get backend URL - use BACKEND_URL if set, otherwise auto-generate from HOST and PORT"""
        if self.BACKEND_URL and self.BACKEND_URL.strip():
            return self.BACKEND_URL
        # Auto-generate from HOST and PORT
        return f"http://localhost:{self.PORT}"


settings = Settings()
