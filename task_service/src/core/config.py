from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/task_db"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    JWT_SECRET_KEY: str = "super-secret-jwt-key-for-development-2025"
    JWT_ALGORITHM: str = "HS256"

    model_config = {"extra": "ignore"}


settings = Settings()