from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TESTING: bool = False
    #DATABASE_URL: str = "postgresql://admin:admin@db:5432/bookstore"
    DATABASE_URL: str = "postgresql://admin:admin@localhost:5432/bookstore"
    JWT_SECRET_KEY: str = "secret_key1234567890qwertyuioplk"


class TestingConfig(Settings):
    TESTING: bool = True
    DATABASE_URL: str = "sqlite:///test.db"
