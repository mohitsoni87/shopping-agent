from typing import TypedDict

from agent_api.schemas.product import ProductResult


class AgentState(TypedDict, total=False):
    tenant_id: str
    env: str
    user_query: str
    semantic_query: str
    size: str | None
    color: str | None
    category: str | None
    price_min: float | None
    price_max: float | None
    query_embedding: list[float]
    results: list[ProductResult]
    search_id: str
    has_more: bool
    answer: str
