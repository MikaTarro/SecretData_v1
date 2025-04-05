# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY pyproject.toml poetry.lock* ./
RUN pip install poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install && poetry show

# Копируем код приложения
COPY . .

# Указываем команду для запуска приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
