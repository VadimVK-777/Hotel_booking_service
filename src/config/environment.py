"""Typed application configuration loaded from environment variables and ``.env``."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class EnvironmentSettings(BaseSettings):
    """Настройки из окружения, используемые Django и сервисами приложения."""

    django_secret_key: str
    django_debug: bool = True
    django_allowed_hosts: str = "localhost,127.0.0.1,[::1],testserver"

    postgres_db: str = "hotel_booking"
    postgres_user: str = "hotel_booking"
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    check_booking_overlaps: bool = True

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def allowed_hosts(self) -> list[str]:
        """Преобразует список хостов через запятую в формат Django."""
        return [host.strip() for host in self.django_allowed_hosts.split(",") if host.strip()]


@lru_cache(maxsize=1)
def get_environment() -> EnvironmentSettings:
    """Загружает и проверяет конфигурацию один раз за время работы процесса."""
    # Обязательные значения поступают из источников pydantic-settings, а не из аргументов.
    return EnvironmentSettings()  # type: ignore[call-arg]
