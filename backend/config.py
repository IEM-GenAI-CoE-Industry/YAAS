from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/YAAS/content/v1"

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8000",
        "http://localhost:5173",
        "https://localhost:5173",
        "http://localhost:5174",
        "https://localhost:5174",
        "http://localhost:5175",
        "https://localhost:5175",
    ]

    PROJECT_NAME: str = "YAAS Platform APIs"

    class Config:
        case_sensitive = True


settings = Settings()