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
    # Комната создаётся через сервис, чтобы единообразно скрыть работу с ORM.
    return Room.objects.create(description=description, price=price)


@transaction.atomic
def delete_room(*, room_id: int) -> None:
    # Блокировка предотвращает удаление комнаты одновременно с другой операцией.
    try:
        room = Room.objects.select_for_update().get(pk=room_id)
    except Room.DoesNotExist as exc:
        raise RoomNotFoundError(room_id) from exc
    room.delete()


@transaction.atomic
def create_booking(*, room_id: int, date_start: date, date_end: date) -> Booking:
    # Блокировка строки комнаты последовательно обрабатывает бронирования этой комнаты.
    # Поэтому проверка пересечений и вставка выполняются как одна безопасная операция.
    try:
        room = Room.objects.select_for_update().get(pk=room_id)
    except Room.DoesNotExist as exc:
        raise RoomNotFoundError(room_id) from exc

    if getattr(settings, "CHECK_BOOKING_OVERLAPS", True):
        # Интервалы пересекаются, если начало одного раньше конца другого
        # и конец первого позже начала второго.
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
    # Блокируем бронирование, чтобы два параллельных удаления не конфликтовали.
    try:
        booking = Booking.objects.select_for_update().get(pk=booking_id)
    except Booking.DoesNotExist as exc:
        raise BookingNotFoundError(booking_id) from exc
    booking.delete()
