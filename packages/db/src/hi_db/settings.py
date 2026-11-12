"""Database settings read from the environment."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://housing:housing@localhost:5440/housing"
    test_database_url: str | None = None
    # Per-process pool. Defaults are SQLAlchemy's; production lowers them because every
    # serverless instance keeps its own pool and the Supabase session pooler caps clients.
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
