FROM python:3.14.2-trixie

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

COPY . .

# Expose port for API service (not used by bot service)
EXPOSE 8000

# Default command (overridden in docker-compose.yml)
CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
