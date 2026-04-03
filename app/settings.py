from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    database_url: str = "sqlite:///./database.db"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    upload_dir: str = "./uploaded_files"
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    auto_create_schema: bool = True

    @validator("cors_allow_origins", pre=True)
    def parse_cors_allow_origins(cls, value):
        if value is None or value == "":
            return ["*"]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    class Config:
        env_prefix = ""
        case_sensitive = False
        fields = {
            "database_url": {"env": "DATABASE_URL"},
            "app_host": {"env": "APP_HOST"},
            "app_port": {"env": "APP_PORT"},
            "upload_dir": {"env": "UPLOAD_DIR"},
            "cors_allow_origins": {"env": "CORS_ALLOW_ORIGINS"},
            "auto_create_schema": {"env": "AUTO_CREATE_SCHEMA"},
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
