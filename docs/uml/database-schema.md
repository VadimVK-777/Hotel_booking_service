# Схема базы данных

```mermaid
erDiagram
    hotel_room ||--o{ hotel_booking : "имеет брони"
    hotel_room {
        bigint id PK
        text description
        numeric_12_2 price
        timestamptz created_at
    }
    hotel_booking {
        bigint id PK
        bigint room_id FK
        date date_start
        date date_end
    }
```

Таблицы соответствуют миграции `hotel.0001_initial`. Все поля обязательны.

- `hotel_room.price` ограничено проверкой `price > 0`.
- `hotel_booking.date_end` должно быть позже `date_start`.
- `hotel_booking.room_id` ссылается на `hotel_room.id`; при удалении номера Django ORM удаляет его брони каскадно.
- Индексы: `(price, id)`, `(created_at, id)` для `hotel_room`; `(room_id, date_start, id)` для `hotel_booking`.
