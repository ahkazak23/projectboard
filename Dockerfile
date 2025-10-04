# ---- Base image ----
FROM python:3.10-slim

# metadata
LABEL authors="ahkazak23"

# ---- Working dir ----
WORKDIR /app

# ---- Copy project files ----
COPY pyproject.toml poetry.lock* ./
RUN pip install poetry && poetry install --no-root --no-interaction --no-ansi

COPY app ./app

# ---- Expose port & run ----
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
