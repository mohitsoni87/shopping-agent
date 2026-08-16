from pydantic import BaseModel

from agent_api.schemas.product import ProductResult


class SearchPageResponse(BaseModel):
    results: list[ProductResult]
    offset: int
    limit: int
    has_more: bool
