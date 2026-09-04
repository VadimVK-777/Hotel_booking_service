# Generated manually for the initial hotel schema.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField()),
                (
                    "price",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_start", models.DateField()),
                ("date_end", models.DateField()),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="hotel.room",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="room",
            constraint=models.CheckConstraint(
                condition=models.Q(("price__gt", 0)),
                name="hotel_room_price_positive",
            ),
        ),
        migrations.AddIndex(
            model_name="room",
            index=models.Index(
                fields=["price", "id"],
                name="hotel_room_price_id_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="room",
            index=models.Index(
                fields=["created_at", "id"],
                name="hotel_room_created_id_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=models.CheckConstraint(
                condition=models.Q(("date_end__gt", models.F("date_start"))),
                name="hotel_booking_dates_ordered",
            ),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["room", "date_start", "id"],
                name="hotel_booking_room_date_idx",
            ),
        ),
    ]
