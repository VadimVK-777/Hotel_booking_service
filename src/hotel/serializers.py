from decimal import Decimal
import re

from rest_framework import serializers

from hotel.models import Booking, Room

DATE_PATTERN = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")


class StrictDateField(serializers.DateField):
    def to_internal_value(self, data):
        if not isinstance(data, str) or DATE_PATTERN.fullmatch(data) is None:
            raise serializers.ValidationError(
                "Date has wrong format. Use YYYY-MM-DD.",
                code="invalid",
            )
        return super().to_internal_value(data)


class RoomCreateSerializer(serializers.Serializer):
    description = serializers.CharField(allow_blank=False, trim_whitespace=True)
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )


class RoomIdSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(min_value=1)


class RoomListQuerySerializer(serializers.Serializer):
    sort_by = serializers.ChoiceField(
        choices=("price", "created_at"),
        default="created_at",
    )
    order = serializers.ChoiceField(choices=("asc", "desc"), default="asc")


class RoomSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Room
        fields = ("room_id", "description", "price", "created_at")


class BookingCreateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(min_value=1)
    date_start = StrictDateField(
        format="%Y-%m-%d",
        input_formats=("%Y-%m-%d",),
    )
    date_end = StrictDateField(
        format="%Y-%m-%d",
        input_formats=("%Y-%m-%d",),
    )

    def validate(self, attrs: dict) -> dict:
        if attrs["date_end"] <= attrs["date_start"]:
            raise serializers.ValidationError(
                "date_end must be later than date_start",
            )
        return attrs


class BookingIdSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(min_value=1)


class BookingSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="id", read_only=True)
    date_start = serializers.DateField(format="%Y-%m-%d")
    date_end = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Booking
        fields = ("booking_id", "date_start", "date_end")
