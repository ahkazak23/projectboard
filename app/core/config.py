from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: int
    DATABASE_URL: str

    # JWT / Auth
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Server
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    # AWS
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str

    # Others
    PROJECT_SIZE_LIMIT_BYTES: int = 10 * 1024 * 1024  # default 10 MB

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
