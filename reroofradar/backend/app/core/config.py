from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://reroofradar:reroofradar_secret@localhost:5432/reroofradar"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-in-production"
    app_env: str = "development"
    mock_services: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
