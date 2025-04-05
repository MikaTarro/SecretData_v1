
FROM python:3.9-slim


WORKDIR /app


COPY pyproject.toml poetry.lock* ./
RUN pip install poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install && poetry show


COPY . .


CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
