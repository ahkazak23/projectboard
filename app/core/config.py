from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URL: Optional[str] = None

    # JWT / Auth
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Server
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    # AWS
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "dummy-bucket"

    # Others
    PROJECT_SIZE_LIMIT_BYTES: int = 10 * 1024 * 1024  # default 10 MB

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
