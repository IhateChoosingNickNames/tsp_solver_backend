from functools import lru_cache
from typing import TypeVar

from pydantic import PostgresDsn, field_validator, AmqpDsn
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


TSettings = TypeVar("TSettings", bound=BaseSettings)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="app_",
        extra="allow",
    )

    debug: bool = True
    origins: str


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="postgres_",
        extra="allow",
    )

    scheme: str
    user: str
    password: str
    host: str
    port: str
    db: str
    url: PostgresDsn | None = None

    @field_validator("url")
    def get_postgres_dsn(
        cls,  # noqa: N805
        value: PostgresDsn | None,
        values: FieldValidationInfo,
    ) -> PostgresDsn:
        if value:
            return value
        return PostgresDsn(
            f"{values.data.get('scheme')}://"
            f"{values.data.get('user')}:"
            f"{values.data.get('password')}@"
            f"{values.data.get('host')}:"
            f"{values.data.get('port')}/"
            f"{values.data.get('db', 'postgres')}",
        )


class RabbitMqSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="rabbitmq_",
        extra="allow",
    )

    default_user: str
    default_pass: str
    host: str
    port: int
    default_vhost: str
    result_queue: str
    url: AmqpDsn | None = None

    @field_validator("url")
    def get_rmq_dsn(
        cls,  # noqa: N805
        value: AmqpDsn | None,
        values: FieldValidationInfo,
    ) -> AmqpDsn:
        if value:
            return value
        return AmqpDsn(
            f"amqp://{values.data.get('default_user')}:"
            f"{values.data.get('default_pass')}@"
            f"{values.data.get('host')}:"
            f"{values.data.get('port')}/"
            f"{values.data.get('default_vhost', '')}",
        )


@lru_cache
def get_settings(cls: type[TSettings]) -> TSettings:
    return cls()
