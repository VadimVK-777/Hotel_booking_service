from datetime import datetime
from decimal import Decimal

from django.utils.dateparse import parse_datetime
import pytest

pytestmark = pytest.mark.django_db


def test_create_room_from_json_returns_generated_id(api_client):
    response = api_client.post(
        "/rooms/create",
        data={"description": "Double room", "price": "149.90"},
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.headers["Content-Type"].startswith("application/json")
    assert set(response.json()) == {"room_id"}
    assert isinstance(response.json()["room_id"], int)
    assert response.json()["room_id"] > 0


def test_create_room_accepts_form_urlencoded(api_client, form_body):
    response = api_client.post(
        "/rooms/create",
        data=form_body({"description": "Single room", "price": "75"}),
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 201
    assert isinstance(response.json()["room_id"], int)


@pytest.mark.parametrize("description", ["", "   "])
def test_create_room_rejects_blank_description(
    api_client,
    assert_json_error,
    description,
):
    response = api_client.post(
        "/rooms/create",
        data={"description": description, "price": "100.00"},
        content_type="application/json",
    )

    assert_json_error(response, 400)


@pytest.mark.parametrize("price", ["0", "-0.01", "not-a-number"])
def test_create_room_rejects_invalid_price(api_client, assert_json_error, price):
    response = api_client.post(
        "/rooms/create",
        data={"description": "Valid description", "price": price},
        content_type="application/json",
    )

    assert_json_error(response, 400)


def test_create_room_rejects_missing_fields(api_client, assert_json_error):
    response = api_client.post(
        "/rooms/create",
        data={"description": "Room without a price"},
        content_type="application/json",
    )

    assert_json_error(response, 400)


def test_room_list_contains_public_fields(api_client, create_room):
    room_id = create_room(description="Sea view", price="101.20")

    response = api_client.get("/rooms/list")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert set(payload[0]) == {"room_id", "description", "price", "created_at"}
    assert payload[0]["room_id"] == room_id
    assert payload[0]["description"] == "Sea view"
    assert payload[0]["price"] == "101.20"
    created_at = parse_datetime(payload[0]["created_at"])
    assert isinstance(created_at, datetime)


def test_room_list_is_empty_initially(api_client):
    response = api_client.get("/rooms/list")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    ("order", "expected_prices"),
    [
        ("asc", [Decimal("10.00"), Decimal("20.00"), Decimal("30.00")]),
        ("desc", [Decimal("30.00"), Decimal("20.00"), Decimal("10.00")]),
    ],
)
def test_room_list_sorts_by_price(api_client, create_room, order, expected_prices):
    create_room(description="Expensive", price="30")
    create_room(description="Cheap", price="10")
    create_room(description="Regular", price="20")

    response = api_client.get(f"/rooms/list?sort_by=price&order={order}")

    assert response.status_code == 200
    prices = [Decimal(item["price"]) for item in response.json()]
    assert prices == expected_prices


@pytest.mark.parametrize("order", ["asc", "desc"])
def test_room_list_sorts_by_creation_time(api_client, create_room, order):
    room_ids = [
        create_room(description="First", price="10"),
        create_room(description="Second", price="20"),
        create_room(description="Third", price="30"),
    ]

    response = api_client.get(f"/rooms/list?sort_by=created_at&order={order}")

    assert response.status_code == 200
    expected = room_ids if order == "asc" else list(reversed(room_ids))
    assert [item["room_id"] for item in response.json()] == expected


def test_room_list_has_stable_secondary_sort(api_client, create_room):
    room_ids = [
        create_room(description="First", price="42"),
        create_room(description="Second", price="42"),
        create_room(description="Third", price="42"),
    ]

    ascending = api_client.get("/rooms/list?sort_by=price&order=asc")
    descending = api_client.get("/rooms/list?sort_by=price&order=desc")

    assert [item["room_id"] for item in ascending.json()] == room_ids
    assert [item["room_id"] for item in descending.json()] == list(reversed(room_ids))


@pytest.mark.parametrize(
    "query",
    ["sort_by=unknown&order=asc", "sort_by=price&order=sideways"],
)
def test_room_list_rejects_invalid_sorting(api_client, assert_json_error, query):
    response = api_client.get(f"/rooms/list?{query}")

    assert_json_error(response, 400)


def test_delete_room_returns_confirmation(api_client, create_room):
    room_id = create_room()

    response = api_client.delete(f"/rooms/delete?room_id={room_id}")

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert api_client.get("/rooms/list").json() == []


def test_delete_room_does_not_delete_other_rooms(api_client, create_room):
    deleted_room_id = create_room(description="Delete me")
    remaining_room_id = create_room(description="Keep me")

    response = api_client.delete(f"/rooms/delete?room_id={deleted_room_id}")

    assert response.status_code == 200
    assert [room["room_id"] for room in api_client.get("/rooms/list").json()] == [remaining_room_id]


@pytest.mark.parametrize("room_id", [999_999, "invalid"])
def test_delete_room_rejects_unknown_or_invalid_id(
    api_client,
    assert_json_error,
    room_id,
):
    response = api_client.delete(f"/rooms/delete?room_id={room_id}")

    expected_status = 404 if isinstance(room_id, int) else 400
    assert_json_error(response, expected_status)
