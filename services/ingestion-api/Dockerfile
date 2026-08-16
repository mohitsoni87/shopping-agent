FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace

# Copy only what this image needs to build: the workspace root (for the lock/
# workspace config), the shared library, and this service. No other service's
# source ever enters this image.
COPY pyproject.toml uv.lock ./
COPY libs/common ./libs/common
COPY services/ingestion-api ./services/ingestion-api

RUN uv sync --frozen --package ingestion-api --no-dev

EXPOSE 8001
CMD ["uv", "run", "uvicorn", "ingestion_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
