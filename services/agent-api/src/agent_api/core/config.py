from functools import lru_cache

from shopping_agent_common.config import CommonSettings


class AgentSettings(CommonSettings):
    """Agent-API-specific settings, layered on top of the common infra settings
    (db, voyage). Only this service depends on the LLM provider - `common`
    stays free of langchain/langgraph so ingestion-api never pulls them in."""

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5"
    search_top_k: int = 5


@lru_cache
def get_agent_settings() -> AgentSettings:
    return AgentSettings()
