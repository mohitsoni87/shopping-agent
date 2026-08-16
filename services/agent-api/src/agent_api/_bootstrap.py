"""Load .env into the process environment before anything else is imported.

Our own settings (AgentSettings/CommonSettings) read .env independently via
pydantic-settings, so they don't need this. But LangSmith tracing is
configured entirely through env vars read directly by the langsmith/
langchain-core SDKs (LANGSMITH_TRACING, LANGSMITH_API_KEY, LANGSMITH_PROJECT,
LANGSMITH_ENDPOINT) - that's not something we route through our own typed
config, so this just makes sure they land in os.environ for local `uv run`
use. In Docker, compose's `env_file: .env` already injects them directly and
this becomes a harmless no-op (no .env file ships inside the image).
"""

from dotenv import load_dotenv

load_dotenv()
