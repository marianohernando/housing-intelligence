"""Database settings read from the environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://housing:housing@localhost:5440/housing"
    test_database_url: str | None = None
