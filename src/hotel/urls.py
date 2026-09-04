from django.urls import path

from hotel.views import (
    BookingCreateView,
    BookingDeleteView,
    BookingListView,
    RoomCreateView,
    RoomDeleteView,
    RoomListView,
)

app_name = "hotel"

urlpatterns = [
    path("rooms/create", RoomCreateView.as_view(), name="room-create"),
    path("rooms/delete", RoomDeleteView.as_view(), name="room-delete"),
    path("rooms/list", RoomListView.as_view(), name="room-list"),
    path("bookings/create", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/delete", BookingDeleteView.as_view(), name="booking-delete"),
    path("bookings/list", BookingListView.as_view(), name="booking-list"),
]
