from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

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

    class Config:
        env_file = ".env"

settings = Settings()