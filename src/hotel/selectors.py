from django.db.models import QuerySet

from hotel.exceptions import RoomNotFoundError
from hotel.models import Booking, Room

ROOM_SORT_FIELDS = {
    "price": "price",
    "created_at": "created_at",
}


def list_rooms(*, sort_by: str, order: str) -> QuerySet[Room]:
    sort_field = ROOM_SORT_FIELDS[sort_by]
    prefix = "-" if order == "desc" else ""
    return Room.objects.order_by(f"{prefix}{sort_field}", f"{prefix}id")


def list_room_bookings(*, room_id: int) -> QuerySet[Booking]:
    if not Room.objects.filter(pk=room_id).exists():
        raise RoomNotFoundError(room_id)
    return Booking.objects.filter(room_id=room_id).order_by("date_start", "id")
