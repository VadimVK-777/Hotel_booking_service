"""Проверка загрузки настроек из окружения и файла .env."""

from pydantic import ValidationError
import pytest

from config.environment import EnvironmentSettings

ENVIRONMENT_KEYS = (
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "CHECK_BOOKING_OVERLAPS",
)


def test_settings_load_and_validate_dotenv_values(tmp_path, monkeypatch):
    # Настройки должны корректно читаться из временного файла .env.
    for key in ENVIRONMENT_KEYS:
        monkeypatch.delenv(key, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DJANGO_SECRET_KEY=dotenv-secret",
                "DJANGO_DEBUG=false",
                "DJANGO_ALLOWED_HOSTS=example.com,api.example.com",
                "POSTGRES_PASSWORD=dotenv-password",
                "POSTGRES_HOST=database.internal",
                "POSTGRES_PORT=6543",
                "CHECK_BOOKING_OVERLAPS=false",
            ]
        ),
        encoding="utf-8",
    )

    settings = EnvironmentSettings(_env_file=env_file)

    assert settings.django_secret_key == "dotenv-secret"
    assert settings.django_debug is False
    assert settings.allowed_hosts == ["example.com", "api.example.com"]
    assert settings.postgres_password == "dotenv-password"
    assert settings.postgres_host == "database.internal"
    assert settings.postgres_port == 6543
    assert settings.check_booking_overlaps is False


def test_environment_variable_has_priority_over_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("POSTGRES_PORT=6543\n", encoding="utf-8")
    monkeypatch.setenv("POSTGRES_PORT", "7654")

    settings = EnvironmentSettings(_env_file=env_file)

    assert settings.postgres_port == 7654


def test_required_secrets_fail_fast_when_configuration_is_missing(monkeypatch):
    for key in ENVIRONMENT_KEYS:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValidationError) as error:
        EnvironmentSettings(_env_file=None)

    missing_fields = {item["loc"][0] for item in error.value.errors()}
    assert missing_fields == {"django_secret_key", "postgres_password"}
