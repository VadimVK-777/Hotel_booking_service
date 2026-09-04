from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from hotel.exceptions import (
    BookingNotFoundError,
    BookingOverlapError,
    RoomNotFoundError,
)
from hotel.models import Booking, Room


def create_room(*, description: str, price: Decimal) -> Room:
    return Room.objects.create(description=description, price=price)


@transaction.atomic
def delete_room(*, room_id: int) -> None:
    try:
        room = Room.objects.select_for_update().get(pk=room_id)
    except Room.DoesNotExist as exc:
        raise RoomNotFoundError(room_id) from exc
    room.delete()


@transaction.atomic
def create_booking(*, room_id: int, date_start: date, date_end: date) -> Booking:
    # Locking the parent row serializes every booking creation for the same room.
    # The overlap check and insert therefore form one concurrency-safe operation.
    try:
        room = Room.objects.select_for_update().get(pk=room_id)
    except Room.DoesNotExist as exc:
        raise RoomNotFoundError(room_id) from exc

    if getattr(settings, "CHECK_BOOKING_OVERLAPS", True):
        overlaps = Booking.objects.filter(
            room=room,
            date_start__lt=date_end,
            date_end__gt=date_start,
        ).exists()
        if overlaps:
            raise BookingOverlapError()

    return Booking.objects.create(
        room=room,
        date_start=date_start,
        date_end=date_end,
    )


@transaction.atomic
def delete_booking(*, booking_id: int) -> None:
    try:
        booking = Booking.objects.select_for_update().get(pk=booking_id)
    except Booking.DoesNotExist as exc:
        raise BookingNotFoundError(booking_id) from exc
    booking.delete()
