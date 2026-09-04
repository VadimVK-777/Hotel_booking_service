from concurrent.futures import ThreadPoolExecutor
import threading

from django.db import close_old_connections, connection, connections
from django.test import Client
import pytest

pytestmark = pytest.mark.django_db(transaction=True)


def test_concurrent_overlapping_requests_create_only_one_booking(create_room):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL is required to verify SELECT FOR UPDATE semantics")

    room_id = create_room(description="Concurrency test room")
    start = threading.Barrier(2)

    def create_overlapping_booking(date_start: str, date_end: str) -> int:
        close_old_connections()
        try:
            start.wait(timeout=5)
            response = Client().post(
                "/bookings/create",
                data={
                    "room_id": room_id,
                    "date_start": date_start,
                    "date_end": date_end,
                },
                content_type="application/json",
            )
            return response.status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(
            create_overlapping_booking,
            "2035-04-10",
            "2035-04-15",
        )
        second = executor.submit(
            create_overlapping_booking,
            "2035-04-12",
            "2035-04-18",
        )

    assert sorted((first.result(), second.result())) == [201, 409]
