FROM ghcr.io/astral-sh/uv:python3.11-alpine

ENV ENV_MODE production
WORKDIR /app

RUN apk add --no-cache curl git \
    # Dependencies for Python package compilation
    freetype-dev \
    gcc \
    musl-dev \
    python3-dev

# Install Python dependencies
COPY pyproject.toml uv.lock ./
ENV UV_LINK_MODE=copy
RUN uv sync --locked --quiet

# Copy application code
COPY . .

# For Cloud Run, use fewer workers since Cloud Run handles horizontal scaling
# Using 1 worker per 2 vCPU is safer for startup and memory
ENV WORKERS=2
ENV THREADS=2
ENV WORKER_CONNECTIONS=1000

ENV PYTHONPATH=/app
EXPOSE 8000

# Gunicorn configuration
CMD ["sh", "-c", "uv run gunicorn api:app \
  --workers $WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 1800 \
  --graceful-timeout 600 \
  --keep-alive 1800 \
  --max-requests 0 \
  --max-requests-jitter 0 \
  --forwarded-allow-ips '*' \
  --worker-connections $WORKER_CONNECTIONS \
  --worker-tmp-dir /dev/shm \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --enable-stdio-inheritance \
  --threads $THREADS"]