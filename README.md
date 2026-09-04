# Hotel Booking Service

Небольшой HTTP JSON API для управления каталогом гостиничных номеров и их
бронированиями. Сервис не требует авторизации, хранит данные в PostgreSQL и запускается
через Docker Compose.

## Возможности

- создание, удаление и сортировка номеров;
- создание, удаление и просмотр броней конкретного номера;
- каскадное удаление броней вместе с номером;
- валидация цены, идентификаторов и календарных дат;
- запрет пересекающихся броней одного номера;
- одинаковый JSON-формат прикладных ошибок;
- приём JSON и `application/x-www-form-urlencoded`;
- постоянное хранение PostgreSQL в Docker volume.

## Стек

- Python 3.12;
- Django и Django REST Framework;
- PostgreSQL 17 и psycopg;
- pydantic-settings;
- Poetry;
- pytest и pytest-django;
- Ruff;
- Gunicorn, Docker и Docker Compose.

## Быстрый запуск через WSL 2

Рекомендуемое окружение для Windows — Ubuntu в WSL 2 и Docker Desktop с включённой
интеграцией с этой WSL-дистрибуцией. Python и PostgreSQL внутри Ubuntu для запуска через
Compose устанавливать не нужно: они находятся в контейнерах.

### Однократная настройка Windows

В PowerShell от имени администратора установите или обновите WSL 2:

```powershell
wsl --install -d Ubuntu
wsl --update
```

После установки перезагрузите Windows. Затем установите Docker Desktop:

```powershell
winget install -e --id Docker.DockerDesktop
```

Если `winget` недоступен, используйте официальный установщик из
[Docker Docs](https://docs.docker.com/desktop/setup/install/windows-install/). Запустите
Docker Desktop и используйте WSL 2 backend. Сам Docker Engine отдельно внутри Ubuntu
устанавливать не требуется.

### Запуск проекта

1. В Docker Desktop откройте `Settings > Resources > WSL Integration`, включите
   интеграцию для Ubuntu и дождитесь состояния `Engine running`.

2. Откройте терминал Ubuntu (WSL) и перейдите в текущий проект на диске Windows:

   ```bash
   cd /mnt/c/Users/VADIM/PycharmProjects/Hotel_booking_service
   ```

3. Запустите проверку окружения. Скрипт проверит WSL, Docker Engine и Compose, а также
   создаст `.env` из примера, если файла ещё нет:

   ```bash
   bash scripts/wsl-check.sh
   ```

4. Откройте `.env` и замените `DJANGO_SECRET_KEY` и `POSTGRES_PASSWORD`:

   ```bash
   nano .env
   ```

5. Соберите и запустите приложение вместе с PostgreSQL:

   ```bash
   docker compose up --build
   ```

После прохождения healthcheck базы и применения миграций API доступен по адресу
`http://localhost:9000`.

Проверка из второго окна WSL:

```bash
curl http://localhost:9000/rooms/list
```

Ожидаемый ответ для пустой базы — `[]`.

Остановка без удаления данных:

```bash
docker compose down
```

PostgreSQL использует именованный volume `postgres_data`, поэтому обычный перезапуск
контейнеров не удаляет номера и брони. Команда ниже намеренно удаляет volume и все данные:

```bash
docker compose down -v
```

Если `docker` доступен в PowerShell, но не находится внутри Ubuntu, повторно включите WSL
Integration в Docker Desktop, затем выполните в PowerShell `wsl --shutdown` и заново
откройте Ubuntu. При использовании Docker Desktop не нужно отдельно устанавливать пакет
`docker.io` внутри WSL.

Проект может работать из `/mnt/c/...`. Для более быстрых операций с большим количеством
файлов рекомендуется после сохранения изменений в Git клонировать репозиторий в файловую
систему WSL, например в `~/projects/Hotel_booking_service`.

## Конфигурация

Настройки загружаются через `pydantic-settings` из корневого файла `.env`. Переменные
окружения имеют приоритет над значениями файла. Образец находится в `.env.example`.

| Переменная | Назначение |
|---|---|
| `DJANGO_SECRET_KEY` | секретный ключ Django |
| `DJANGO_DEBUG` | режим отладки (`true` или `false`) |
| `DJANGO_ALLOWED_HOSTS` | разрешённые хосты через запятую |
| `POSTGRES_DB` | имя базы данных |
| `POSTGRES_USER` | пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | пароль PostgreSQL |
| `POSTGRES_HOST` | хост БД при локальном запуске |
| `POSTGRES_PORT` | порт PostgreSQL для локального приложения и на хосте Compose |
| `CHECK_BOOKING_OVERLAPS` | включение проверки пересечений броней |

В Compose значение `POSTGRES_HOST` для контейнера приложения принудительно равно `db`.

## API

Все URL указаны без завершающего `/`. В теле успешного ответа и ответа с ошибкой всегда
возвращается JSON.

| Метод | URL | Параметры | Код успешного ответа |
|---|---|---|---:|
| `POST` | `/rooms/create` | `description`, `price` | `201` |
| `DELETE` | `/rooms/delete?room_id={id}` | `room_id` | `200` |
| `GET` | `/rooms/list` | `sort_by`, `order` | `200` |
| `POST` | `/bookings/create` | `room_id`, `date_start`, `date_end` | `201` |
| `DELETE` | `/bookings/delete?booking_id={id}` | `booking_id` | `200` |
| `GET` | `/bookings/list?room_id={id}` | `room_id` | `200` |

### Создать номер

```bash
curl -X POST http://localhost:9000/rooms/create \
  -H "Content-Type: application/json" \
  -d '{"description":"Double room with a city view","price":"149.90"}'
```

Ответ:

```json
{"room_id": 24}
```

Описание не может быть пустым, а цена должна быть положительной. Для цены используется
десятичный тип, поэтому ошибки двоичного `float` при денежных расчётах не возникают.

### Удалить номер

```bash
curl -X DELETE "http://localhost:9000/rooms/delete?room_id=24"
```

Ответ:

```json
{"deleted": true}
```

Все брони этого номера удаляются каскадно.

### Получить список номеров

```bash
curl "http://localhost:9000/rooms/list?sort_by=price&order=desc"
```

Ответ:

```json
[
  {
    "room_id": 24,
    "description": "Double room with a city view",
    "price": "149.90",
    "created_at": "2030-01-15T10:30:00Z"
  }
]
```

Параметр `sort_by` принимает `price` или `created_at`, а `order` — `asc` или `desc`.
Значения по умолчанию: `created_at` и `asc`. При равных значениях используется ID как
вторичный ключ, поэтому порядок стабилен. Цена в ответе представлена строкой с двумя
знаками после точки для сохранения точности.

### Создать бронь

JSON-запрос:

```bash
curl -X POST http://localhost:9000/bookings/create \
  -H "Content-Type: application/json" \
  -d '{"room_id":24,"date_start":"2031-06-20","date_end":"2031-06-25"}'
```

Вариант, совместимый с `curl -d` из условия задачи:

```bash
curl -X POST \
  -d "room_id=24" \
  -d "date_start=2031-06-20" \
  -d "date_end=2031-06-25" \
  http://localhost:9000/bookings/create
```

Ответ:

```json
{"booking_id": 1444}
```

Даты должны быть реальными календарными датами строго в формате `YYYY-MM-DD`, а
`date_end` должна быть позже `date_start`.

### Удалить бронь

```bash
curl -X DELETE "http://localhost:9000/bookings/delete?booking_id=1444"
```

Ответ:

```json
{"deleted": true}
```

### Получить брони номера

```bash
curl "http://localhost:9000/bookings/list?room_id=24"
```

Ответ отсортирован по дате начала, затем по ID:

```json
[
  {
    "booking_id": 1444,
    "date_start": "2031-06-20",
    "date_end": "2031-06-25"
  }
]
```

Для существующего номера без броней возвращается пустой массив. Для несуществующего
номера возвращается `404`, что позволяет отличить эти ситуации.

## Ошибки

Единый формат ошибки:

```json
{"error": "Room not found"}
```

Используемые HTTP-коды:

- `400 Bad Request` — отсутствует или не прошёл валидацию параметр;
- `404 Not Found` — номер или бронь не существует;
- `409 Conflict` — даты пересекаются с существующей бронью;
- `405 Method Not Allowed` — хендлер вызван неподдерживаемым HTTP-методом;
- `500 Internal Server Error` — непредвиденная внутренняя ошибка без раскрытия traceback.

## Правила бронирования и принятые решения

- Интервал проживания трактуется как полуоткрытый: `[date_start, date_end)`. Поэтому бронь
  `20–25 июня` не конфликтует с бронями `15–20 июня` и `25–30 июня`.
- Пересечение существует, если начало имеющейся брони раньше конца новой и её конец позже
  начала новой. Проверка выполняется только среди броней того же номера.
- Создание брони выполняется в транзакции с блокировкой строки номера. Это защищает проверку
  от одновременных конкурирующих запросов.
- Ограничение пересечений обеспечивается сервисным слоем. Прямые записи через raw SQL в обход
  API должны самостоятельно соблюдать это правило.
- Даты в прошлом разрешены: запрета на них в исходном контракте нет.
- Поле `cbooking_id` из одного примера считается опечаткой; API возвращает согласованное
  поле `booking_id`.
- Пагинация в первой версии отсутствует, чтобы ответ списка соответствовал заданному
  JSON-массиву.
- Схема создаётся стандартными Django migrations. Внешний ключ брони настроен с каскадным
  удалением; ограничения цены и порядка дат продублированы на уровне базы данных.

## Локальная разработка

Понадобятся Python 3.12, Poetry и доступный PostgreSQL. Установите зависимости и создайте
конфигурацию:

```bash
poetry install
cp .env.example .env
```

Можно поднять только PostgreSQL из Compose. Его порт на хосте и порт подключения локального
Django задаются одной переменной `POSTGRES_PORT`; внутри сети Compose приложение всегда
подключается к стандартному порту `5432`:

```bash
docker compose up -d db
poetry run python src/manage.py migrate
poetry run python src/manage.py runserver 0.0.0.0:9000
```

Полезные команды также доступны через Makefile:

```bash
make wsl-check
make wsl-up
make compose-ps
make compose-logs
make migrate
make run
make lint
make fmt-check
make test
```

## Тесты

Тесты используют отдельную временную базу, которую создаёт `pytest-django`; рабочие данные
не изменяются. PostgreSQL из Compose должен быть доступен на хосте, а значения
`POSTGRES_*` должны совпадать с `.env`:

```bash
docker compose up -d db
poetry install --with dev
poetry run pytest
```

После изменения `pyproject.toml` или `poetry.lock` повторно выполняйте
`poetry install --with dev`. Иначе старое виртуальное окружение может содержать pytest,
но не содержать `pytest-django`, `pydantic` или других новых зависимостей. Команда
`make check` теперь проверяет наличие обязательных пакетов до запуска линтеров и тестов.

Проверка с покрытием и полный локальный quality gate:

```bash
poetry run pytest --cov=src --cov-report=term-missing
make check
```

Набор тестов проверяет оба формата входа, CRUD, сортировку, каскадное удаление, ошибки,
валидацию дат и цены, все основные виды пересечений и разрешённые соседние интервалы.
GitHub Actions выполняет этот набор на PostgreSQL, включая конкурентное создание двух
пересекающихся броней.

## Структура проекта

```text
.
├── compose.yaml
├── .github/workflows/ci.yml
├── docker/
├── scripts/wsl-check.sh # проверка Docker Desktop integration внутри WSL
├── src/
│   ├── config/          # конфигурация Django и загрузка окружения
│   ├── hotel/           # модели, сериализаторы, сервисы, выборки и HTTP-хендлеры
│   └── manage.py
├── tests/               # контрактные и интеграционные API-тесты
├── .env.example
├── Dockerfile
├── Makefile
└── pyproject.toml
```
