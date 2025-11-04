FROM python:3.10-slim
WORKDIR /app

# bağımlılıklar
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# uygulama
COPY app ./app
COPY alembic.ini ./

EXPOSE 8000

# ---- Run server ----
CMD poetry run uvicorn app.main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000}
