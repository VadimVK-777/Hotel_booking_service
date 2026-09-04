from django.db import models
from django.db.models import F, Q


class Room(models.Model):
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="hotel_room_price_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["price", "id"], name="hotel_room_price_id_idx"),
            models.Index(fields=["created_at", "id"], name="hotel_room_created_id_idx"),
        ]

    def __str__(self) -> str:
        return f"Room {self.pk}"


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    date_start = models.DateField()
    date_end = models.DateField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(date_end__gt=F("date_start")),
                name="hotel_booking_dates_ordered",
            ),
        ]
        indexes = [
            models.Index(
                fields=["room", "date_start", "id"],
                name="hotel_booking_room_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Booking {self.pk} for room {self.room_id}"
