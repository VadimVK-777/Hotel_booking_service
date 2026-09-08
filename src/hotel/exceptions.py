class HotelDomainError(Exception):
    """Base exception for expected hotel domain failures."""


class RoomNotFoundError(HotelDomainError):
    def __init__(self, room_id: int) -> None:
        super().__init__(f"Room with id {room_id} was not found")


class BookingNotFoundError(HotelDomainError):
    def __init__(self, booking_id: int) -> None:
        super().__init__(f"Booking with id {booking_id} was not found")


class BookingOverlapError(HotelDomainError):
    def __init__(self) -> None:
        super().__init__("Room is already booked for the requested dates")
