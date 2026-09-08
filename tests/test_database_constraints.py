"""Проверка ограничений базы данных для комнат и бронирований."""

from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
import pytest

from hotel.models import Booking, Room

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("price", [Decimal("0.00"), Decimal("-1.00")])
def test_database_rejects_non_positive_room_price(price):
    # Цена комнаты обязана быть строго положительной.
    with pytest.raises(IntegrityError), transaction.atomic():
        Room.objects.create(description="Invalid room", price=price)


@pytest.mark.parametrize(
    ("date_start", "date_end"),
    [(date(2031, 6, 20), date(2031, 6, 20)), (date(2031, 6, 21), date(2031, 6, 20))],
)
def test_database_rejects_invalid_booking_date_order(date_start, date_end):
    room = Room.objects.create(description="Valid room", price=Decimal("100.00"))

    with pytest.raises(IntegrityError), transaction.atomic():
        Booking.objects.create(room=room, date_start=date_start, date_end=date_end)


def test_database_cascades_booking_deletion_with_room():
    room = Room.objects.create(description="Room", price=Decimal("100.00"))
    booking = Booking.objects.create(
        room=room,
        date_start=date(2031, 6, 20),
        date_end=date(2031, 6, 25),
    )

    room.delete()

    assert not Booking.objects.filter(pk=booking.pk).exists()
