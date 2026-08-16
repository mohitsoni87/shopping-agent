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
