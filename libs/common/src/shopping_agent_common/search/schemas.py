from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ItemMatch:
    size: str | None
    color: str | None
    price: float | None
    stock: int


@dataclass(frozen=True, slots=True)
class ProductMatch:
    title: str
    description: str
    category: str | None
    image_url: str | None
    items: list[ItemMatch] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SearchPage:
    matches: list[ProductMatch]
    offset: int
    limit: int
    has_more: bool
