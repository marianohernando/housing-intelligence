"""API settings from the environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://housing:housing@localhost:5440/housing"
    cors_origins: list[str] = ["http://localhost:3010"]
