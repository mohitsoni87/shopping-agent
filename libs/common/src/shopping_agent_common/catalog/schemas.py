from enum import StrEnum

from pydantic import BaseModel, Field

from shopping_agent_common.product_types import Gender


class ItemUpsert(BaseModel):
    external_item_id: str
    size: str | None = None
    color: str | None = None
    price: float | None = None
    stock: int = 0


class ProductUpsert(BaseModel):
    external_product_id: str
    title: str
    description: str
    category: str | None = None
    gender: Gender | None = None
    image_url: str | None = None
    attributes: dict = Field(default_factory=dict)
    items: list[ItemUpsert] = Field(default_factory=list)


class UpsertOutcome(StrEnum):
    """What CatalogService.upsert_product actually did - lets callers (the
    ingestion webhook, the seed CLI) report a meaningful summary instead of
    treating every call as a write."""

    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
