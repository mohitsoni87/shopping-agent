FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY libs/common ./libs/common
COPY services/agent-api ./services/agent-api

RUN uv sync --frozen --package agent-api --no-dev

EXPOSE 8002
CMD ["uv", "run", "uvicorn", "agent_api.main:app", "--host", "0.0.0.0", "--port", "8002"]
