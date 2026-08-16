from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Infrastructure-level settings shared by every service: how to reach the
    Feature Store (Postgres) and the embedding provider. Service-specific settings
    (LLM provider, model choice, request tuning) live in each service's own
    `core/config.py` and subclass this.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/shopping_agent"
    voyage_api_key: str = ""
    voyage_model: str = "voyage-3"
    embedding_dim: int = 1024


@lru_cache
def get_common_settings() -> CommonSettings:
    return CommonSettings()
