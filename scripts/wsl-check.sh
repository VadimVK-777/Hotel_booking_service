#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -z "${WSL_DISTRO_NAME:-}" ]]; then
    echo "Ошибка: запустите этот скрипт внутри WSL (например, Ubuntu)." >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Ошибка: команда docker недоступна внутри WSL." >&2
    echo "В Docker Desktop включите Settings > Resources > WSL Integration для ${WSL_DISTRO_NAME}." >&2
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Ошибка: недоступен плагин Docker Compose." >&2
    echo "Обновите Docker Desktop и перезапустите WSL." >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Ошибка: Docker Engine не отвечает." >&2
    echo "Запустите Docker Desktop и дождитесь состояния Engine running." >&2
    exit 1
fi

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"

if [[ ! -f .env ]]; then
    cp .env.example .env
    echo "Создан .env из .env.example. Перед публичным запуском замените секреты."
fi

echo "WSL: ${WSL_DISTRO_NAME}"
echo "Проект: ${project_dir}"
echo "Docker и Compose готовы. Запуск: docker compose -f docker-compose.yaml up --build"
