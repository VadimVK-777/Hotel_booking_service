from collections.abc import Mapping
import logging
from typing import Any

from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ParseError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hotel import selectors, services
from hotel.exceptions import (
    BookingNotFoundError,
    BookingOverlapError,
    RoomNotFoundError,
)
from hotel.serializers import (
    BookingCreateSerializer,
    BookingIdSerializer,
    BookingSerializer,
    RoomCreateSerializer,
    RoomIdSerializer,
    RoomListQuerySerializer,
    RoomSerializer,
)

logger = logging.getLogger(__name__)


def _first_error(value: Any) -> str:
    if isinstance(value, dict):
        if not value:
            return "Request failed"
        key, nested = next(iter(value.items()))
        message = _first_error(nested)
        if key in {"detail", "non_field_errors"}:
            return message
        return f"{key}: {message}"
    if isinstance(value, (list, tuple)):
        if not value:
            return "Request failed"
        return _first_error(value[0])
    if isinstance(value, ErrorDetail):
        return str(value)
    return str(value)


def _request_data(request: Request) -> dict[str, Any]:
    """Read JSON/form body and use query parameters as a fallback."""
    if not isinstance(request.data, Mapping):
        raise ParseError("Request body must be a JSON object")
    data = {key: value for key, value in request.data.items()}
    for key, value in request.query_params.items():
        data.setdefault(key, value)
    return data


class HotelAPIView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def handle_exception(self, exc: Exception) -> Response:
        try:
            response = super().handle_exception(exc)
        except Exception:
            logger.exception("Unhandled hotel API error")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response.data = {"error": _first_error(response.data)}
        return response


class RoomCreateView(HotelAPIView):
    def post(self, request: Request) -> Response:
        serializer = RoomCreateSerializer(data=_request_data(request))
        serializer.is_valid(raise_exception=True)
        room = services.create_room(**serializer.validated_data)
        return Response(
            {"room_id": room.pk},
            status=status.HTTP_201_CREATED,
        )


class RoomDeleteView(HotelAPIView):
    def delete(self, request: Request) -> Response:
        serializer = RoomIdSerializer(data=_request_data(request))
        serializer.is_valid(raise_exception=True)
        try:
            services.delete_room(**serializer.validated_data)
        except RoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"deleted": True}, status=status.HTTP_200_OK)


class RoomListView(HotelAPIView):
    def get(self, request: Request) -> Response:
        query_serializer = RoomListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        rooms = selectors.list_rooms(**query_serializer.validated_data)
        return Response(RoomSerializer(rooms, many=True).data)


class BookingCreateView(HotelAPIView):
    def post(self, request: Request) -> Response:
        serializer = BookingCreateSerializer(data=_request_data(request))
        serializer.is_valid(raise_exception=True)
        try:
            booking = services.create_booking(**serializer.validated_data)
        except RoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except BookingOverlapError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(
            {"booking_id": booking.pk},
            status=status.HTTP_201_CREATED,
        )


class BookingDeleteView(HotelAPIView):
    def delete(self, request: Request) -> Response:
        serializer = BookingIdSerializer(data=_request_data(request))
        serializer.is_valid(raise_exception=True)
        try:
            services.delete_booking(**serializer.validated_data)
        except BookingNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"deleted": True}, status=status.HTTP_200_OK)


class BookingListView(HotelAPIView):
    def get(self, request: Request) -> Response:
        serializer = RoomIdSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        try:
            bookings = selectors.list_room_bookings(**serializer.validated_data)
        except RoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookingSerializer(bookings, many=True).data)
