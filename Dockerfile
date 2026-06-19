FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    uv sync --frozen --no-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN chmod +x scripts/*.sh

EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
