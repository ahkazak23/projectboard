# ---- Base image ----
FROM python:3.10-slim

# metadata
LABEL authors="ahkazak23"

# ---- Working dir ----
WORKDIR /app

# ---- Copy project files ----
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# ---- Copy source code ----
COPY app ./app

# ---- Expose port ----
EXPOSE 8000

# ---- Run server ----
CMD poetry run uvicorn app.main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000}
