"""API settings from the environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    database_url: str = "postgresql+psycopg://housing:housing@localhost:5440/housing"
    cors_origins: list[str] = ["http://localhost:3010"]
    # D-250, the search by parcel. PARCEL_UPSTREAMS=false: no call to the Catastro, the
    # Ayuntamiento or CartoCiudad; only the demo parcels, from their saved sheets (offline, e2e).
    parcel_upstreams: bool = True
    # Lookups per IP and minute that call the Catastro or the Ayuntamiento (cache misses only),
    # and CartoCiudad's for the address box; over it, 429 with Retry-After.
    parcel_guard_per_minute: int = 20
    geocoder_guard_per_minute: int = 60
