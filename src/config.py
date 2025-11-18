from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()