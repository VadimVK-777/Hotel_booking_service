"""Тесты API бронирований: валидация, пересечения дат и каскадное удаление."""

import pytest

pytestmark = pytest.mark.django_db


def test_create_booking_from_json_returns_generated_id(api_client, room_id):
    # Успешное бронирование возвращает новый идентификатор записи.
    response = api_client.post(
        "/bookings/create",
        data={
            "room_id": room_id,
            "date_start": "2031-06-20",
            "date_end": "2031-06-25",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.headers["Content-Type"].startswith("application/json")
    assert set(response.json()) == {"booking_id"}
    assert isinstance(response.json()["booking_id"], int)
    assert response.json()["booking_id"] > 0


def test_create_booking_accepts_form_urlencoded(api_client, form_body, room_id):
    response = api_client.post(
        "/bookings/create",
        data=form_body(
            {
                "room_id": room_id,
                "date_start": "2031-06-20",
                "date_end": "2031-06-25",
            }
        ),
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 201
    assert isinstance(response.json()["booking_id"], int)


def test_create_booking_rejects_unknown_room(api_client, assert_json_error):
    response = api_client.post(
        "/bookings/create",
        data={
            "room_id": 999_999,
            "date_start": "2031-06-20",
            "date_end": "2031-06-25",
        },
        content_type="application/json",
    )

    assert_json_error(response, 404)


@pytest.mark.parametrize(
    ("date_start", "date_end"),
    [
        ("not-a-date", "2031-06-25"),
        ("2031-02-30", "2031-03-01"),
        ("2031/06/20", "2031-06-25"),
        ("2031-6-20", "2031-06-25"),
        ("2031-06-2", "2031-06-25"),
        ("2031-06-20", "not-a-date"),
    ],
)
def test_create_booking_rejects_invalid_dates(
    api_client,
    assert_json_error,
    room_id,
    date_start,
    date_end,
):
    response = api_client.post(
        "/bookings/create",
        data={"room_id": room_id, "date_start": date_start, "date_end": date_end},
        content_type="application/json",
    )

    assert_json_error(response, 400)


@pytest.mark.parametrize(
    ("date_start", "date_end"),
    [("2031-06-20", "2031-06-20"), ("2031-06-21", "2031-06-20")],
)
def test_create_booking_requires_end_after_start(
    api_client,
    assert_json_error,
    room_id,
    date_start,
    date_end,
):
    response = api_client.post(
        "/bookings/create",
        data={"room_id": room_id, "date_start": date_start, "date_end": date_end},
        content_type="application/json",
    )

    assert_json_error(response, 400)


def test_booking_list_is_sorted_by_start_date(api_client, room_id, create_booking):
    booking_ids = {
        "middle": create_booking(room_id, "2031-06-20", "2031-06-22"),
        "last": create_booking(room_id, "2031-07-01", "2031-07-03"),
        "first": create_booking(room_id, "2031-05-01", "2031-05-04"),
    }

    response = api_client.get(f"/bookings/list?room_id={room_id}")

    assert response.status_code == 200
    assert response.json() == [
        {
            "booking_id": booking_ids["first"],
            "date_start": "2031-05-01",
            "date_end": "2031-05-04",
        },
        {
            "booking_id": booking_ids["middle"],
            "date_start": "2031-06-20",
            "date_end": "2031-06-22",
        },
        {
            "booking_id": booking_ids["last"],
            "date_start": "2031-07-01",
            "date_end": "2031-07-03",
        },
    ]


def test_booking_list_is_empty_for_existing_room(api_client, room_id):
    response = api_client.get(f"/bookings/list?room_id={room_id}")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("room_id", [999_999, "invalid"])
def test_booking_list_rejects_unknown_or_invalid_room(
    api_client,
    assert_json_error,
    room_id,
):
    response = api_client.get(f"/bookings/list?room_id={room_id}")

    expected_status = 404 if isinstance(room_id, int) else 400
    assert_json_error(response, expected_status)


def test_delete_booking_returns_confirmation(api_client, room_id, create_booking):
    booking_id = create_booking(room_id)

    response = api_client.delete(f"/bookings/delete?booking_id={booking_id}")

    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    assert api_client.get(f"/bookings/list?room_id={room_id}").json() == []


@pytest.mark.parametrize("booking_id", [999_999, "invalid"])
def test_delete_booking_rejects_unknown_or_invalid_id(
    api_client,
    assert_json_error,
    booking_id,
):
    response = api_client.delete(f"/bookings/delete?booking_id={booking_id}")

    expected_status = 404 if isinstance(booking_id, int) else 400
    assert_json_error(response, expected_status)


def test_deleting_room_cascades_to_its_bookings(api_client, room_id, create_booking):
    booking_id = create_booking(room_id)

    room_response = api_client.delete(f"/rooms/delete?room_id={room_id}")
    booking_response = api_client.delete(f"/bookings/delete?booking_id={booking_id}")

    assert room_response.status_code == 200
    assert_json_error_payload(booking_response, expected_status=404)


def assert_json_error_payload(response, expected_status: int) -> None:
    assert response.status_code == expected_status
    assert response.headers["Content-Type"].startswith("application/json")
    assert set(response.json()) == {"error"}


@pytest.mark.parametrize(
    ("date_start", "date_end"),
    [
        ("2031-06-23", "2031-06-27"),
        ("2031-06-18", "2031-06-21"),
        ("2031-06-21", "2031-06-24"),
        ("2031-06-18", "2031-06-27"),
        ("2031-06-20", "2031-06-25"),
    ],
)
def test_create_booking_rejects_every_kind_of_overlap(
    api_client,
    assert_json_error,
    room_id,
    create_booking,
    date_start,
    date_end,
):
    # Любое пересечение интервалов с существующим бронированием запрещено.
    create_booking(room_id, "2031-06-20", "2031-06-25")

    response = api_client.post(
        "/bookings/create",
        data={"room_id": room_id, "date_start": date_start, "date_end": date_end},
        content_type="application/json",
    )

    assert_json_error(response, 409)


def test_create_booking_allows_adjacent_intervals(api_client, room_id, create_booking):
    create_booking(room_id, "2031-06-20", "2031-06-25")

    before = api_client.post(
        "/bookings/create",
        data={
            "room_id": room_id,
            "date_start": "2031-06-15",
            "date_end": "2031-06-20",
        },
        content_type="application/json",
    )
    after = api_client.post(
        "/bookings/create",
        data={
            "room_id": room_id,
            "date_start": "2031-06-25",
            "date_end": "2031-06-30",
        },
        content_type="application/json",
    )

    assert before.status_code == 201
    assert after.status_code == 201


def test_same_dates_can_be_booked_for_different_rooms(api_client, create_room, create_booking):
    first_room = create_room(description="First room")
    second_room = create_room(description="Second room")

    first_booking = create_booking(first_room, "2031-06-20", "2031-06-25")
    second_booking = create_booking(second_room, "2031-06-20", "2031-06-25")

    assert first_booking != second_booking
