from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="database_")

    connection_string: str = Field()
    connection_pool_size: int = 5
    connection_pool_max_overflow: int = 10


DATABASE_SETTINGS = _DatabaseSettings()
