from pydantic import BaseModel


class ItemResult(BaseModel):
    size: str | None
    color: str | None
    price: float | None
    stock: int


class ProductResult(BaseModel):
    title: str
    description: str
    category: str | None
    image_url: str | None
    items: list[ItemResult]
