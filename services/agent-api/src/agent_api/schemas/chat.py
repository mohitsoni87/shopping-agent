from pydantic import BaseModel

from agent_api.schemas.product import ProductResult


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    search_id: str | None = None
    results: list[ProductResult] = []
    offset: int = 0
    limit: int = 0
    has_more: bool = False
