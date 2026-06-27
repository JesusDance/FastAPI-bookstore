import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    REDIS_URL: str = os.getenv("REDIS_URL")
    ORIGINS: list = ["http://127.0.0.1:3000", "http://localhost:8080"]
    CACHE_TTL_SECONDS: int = 3600
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
