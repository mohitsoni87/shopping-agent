from pydantic import BaseModel

from agent_api.schemas.product import ProductResult


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    search_id: str
    answer: str
    results: list[ProductResult]
    offset: int
    limit: int
    has_more: bool
