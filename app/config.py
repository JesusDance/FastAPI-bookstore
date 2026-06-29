from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str 
    JWT_SECRET_KEY: str 
    ALGORITHM: str 
    REDIS_URL: str
    ADMIN_NAME: str
    ADMIN_PASS: str

    ORIGINS: list[str] = ["http://127.0.0.1:3000", "http://localhost:8080"]
    CACHE_TTL_SECONDS: int = 3600
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CACHE_EX_SECONDS: int = 60
    LIMIT_OF_REQUESTS: int = 5


settings = Settings()
