from shopping_agent_common.search import ProductMatch

from agent_api.schemas.product import ItemResult, ProductResult


def serialize_product_matches(matches: list[ProductMatch]) -> list[ProductResult]:
    return [
        ProductResult(
            title=match.title,
            description=match.description,
            category=match.category,
            image_url=match.image_url,
            items=[
                ItemResult(size=i.size, color=i.color, price=i.price, stock=i.stock)
                for i in match.items
            ],
        )
        for match in matches
    ]
