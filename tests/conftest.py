from collections.abc import Callable
import os
from urllib.parse import urlencode

import pytest

# Configuration is evaluated while Django is initialized by pytest-django. Keep the
# suite runnable both inside Docker Compose and against a developer's local PostgreSQL.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("DJANGO_DEBUG", "false")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
os.environ.setdefault("POSTGRES_DB", "hotel_booking")
os.environ.setdefault("POSTGRES_USER", "hotel_booking")
os.environ.setdefault("POSTGRES_PASSWORD", "hotel_booking")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("CHECK_BOOKING_OVERLAPS", "true")


@pytest.fixture
def api_client():
    from django.test import Client

    return Client()


@pytest.fixture
def create_room(api_client) -> Callable[..., int]:
    def factory(description: str = "Room with a city view", price: str = "125.50") -> int:
        response = api_client.post(
            "/rooms/create",
            data={"description": description, "price": price},
            content_type="application/json",
        )
        assert response.status_code == 201, response.content
        return response.json()["room_id"]

    return factory


@pytest.fixture
def room_id(create_room) -> int:
    return create_room()


@pytest.fixture
def create_booking(api_client) -> Callable[..., int]:
    def factory(
        room_id: int,
        date_start: str = "2030-01-10",
        date_end: str = "2030-01-15",
    ) -> int:
        response = api_client.post(
            "/bookings/create",
            data={
                "room_id": room_id,
                "date_start": date_start,
                "date_end": date_end,
            },
            content_type="application/json",
        )
        assert response.status_code == 201, response.content
        return response.json()["booking_id"]

    return factory


@pytest.fixture
def assert_json_error() -> Callable[..., None]:
    def assertion(response, expected_status: int) -> None:
        assert response.status_code == expected_status
        assert response.headers["Content-Type"].startswith("application/json")
        payload = response.json()
        assert set(payload) == {"error"}
        assert isinstance(payload["error"], str)
        assert payload["error"].strip()

    return assertion


@pytest.fixture
def form_body() -> Callable[[dict[str, object]], str]:
    return urlencode
