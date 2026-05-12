FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY mock-infra/app/pyproject.toml app/

RUN uv sync --frozen --no-dev

COPY mock-infra/app app

WORKDIR /app/app

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]