FROM python:3.12-slim

# Отправка вывода Python напрямую в консоль (для логирования)
ENV PYTHONUNBUFFERED=1

# Копирование uv-бинарников из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Сначала копируем файлы зависимостей (pyproject.toml, uv.lock и т.п.),
# чтобы воспользоваться кэшированием Docker-слоёв.
COPY pyproject.toml uv.lock ./

# Устанавливаем управляемую версию Python в виртуальное окружение.
RUN uv python install 3.12

# Синхронизируем зависимости — создаётся полноценное виртуальное окружение (.venv)
RUN uv sync --frozen --no-cache

# Теперь копируем оставшиеся файлы приложения.
COPY . .

# Expose порта 80 (опционально, для доступа к документации Swagger)
EXPOSE 80

# Запускаем FastAPI через команду fastapi внутри созданного виртуального окружения.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
