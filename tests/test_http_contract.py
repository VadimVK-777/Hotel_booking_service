"""Проверка общего HTTP-контракта обработчиков и формата ошибок."""

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/rooms/create"),
        ("POST", "/rooms/delete"),
        ("POST", "/rooms/list"),
        ("GET", "/bookings/create"),
        ("POST", "/bookings/delete"),
        ("POST", "/bookings/list"),
    ],
)
def test_handlers_reject_unsupported_http_methods(
    api_client,
    assert_json_error,
    method,
    path,
):
    # Каждый обработчик принимает только предусмотренный HTTP-метод.
    response = api_client.generic(method, path)

    assert_json_error(response, 405)


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("DELETE", "/rooms/delete"),
        ("GET", "/bookings/list"),
        ("DELETE", "/bookings/delete"),
    ],
)
def test_handlers_reject_missing_query_ids(
    api_client,
    assert_json_error,
    method,
    path,
):
    response = api_client.generic(method, path)

    assert_json_error(response, 400)


def test_malformed_json_returns_json_error(api_client, assert_json_error):
    response = api_client.post(
        "/rooms/create",
        data='{"description":',
        content_type="application/json",
    )

    assert_json_error(response, 400)


@pytest.mark.parametrize("path", ["/unknown", "/rooms/list/"])
def test_unknown_routes_return_json_error(api_client, assert_json_error, path):
    response = api_client.get(path)

    assert_json_error(response, 404)


def test_unexpected_handler_failure_returns_safe_json_error(
    api_client,
    assert_json_error,
    monkeypatch,
):
    def fail_to_create_room(**_kwargs):
        raise RuntimeError("sensitive internal details")

    monkeypatch.setattr("hotel.views.services.create_room", fail_to_create_room)

    response = api_client.post(
        "/rooms/create",
        data={"description": "Room", "price": "100.00"},
        content_type="application/json",
    )

    assert_json_error(response, 500)
    assert "sensitive internal details" not in response.json()["error"]
