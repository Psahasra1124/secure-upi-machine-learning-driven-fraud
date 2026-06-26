from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Secure UPI"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "development-only-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./secure_upi.db"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173",
        "https://secure-upi-machine-learning-driven.vercel.app"]
    )
    model_path: Path = Path("../ml/artifacts/fraud_model.joblib")
    model_metadata_path: Path = Path("../ml/artifacts/model_metadata.json")
    admin_email: str = "admin@secureupi.com"
    admin_password: str = "ChangeMe123!"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
