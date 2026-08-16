from sqlalchemy.orm import Session

from shopping_agent_common.product_types import Gender
from shopping_agent_common.repositories import ItemFilters, ItemRepository, ProductRepository
from shopping_agent_common.search.schemas import ItemMatch, ProductMatch, SearchPage


class SearchService:
    """Read path for the Feature Store: natural-language-derived vector search
    over products, narrowed by structured item-level filters (size/color/price/
    stock) and an optional product category."""

    def __init__(self, session: Session):
        self._products = ProductRepository(session)
        self._items = ItemRepository(session)

    def search_products(
        self,
        *,
        tenant_id: str,
        env: str,
        query_embedding: list[float],
        item_filters: ItemFilters,
        category: str | None = None,
        gender: Gender | None = None,
        limit: int = 5,
        offset: int = 0,
    ) -> SearchPage:
        has_matching_item = self._items.exists_for_product(tenant_id, env, item_filters)

        # Fetch one extra row to detect whether a next page exists, without a
        # separate COUNT(*) query.
        products = self._products.search_by_similarity(
            tenant_id=tenant_id,
            env=env,
            query_embedding=query_embedding,
            category=category,
            gender=gender,
            has_matching_item=has_matching_item,
            limit=limit + 1,
            offset=offset,
        )
        has_more = len(products) > limit
        products = products[:limit]

        matches = []
        for product in products:
            items = self._items.list_for_product(product.id, tenant_id, env, item_filters)
            item_matches = [
                ItemMatch(
                    size=item.size,
                    color=item.color,
                    price=float(item.price) if item.price is not None else None,
                    stock=item.stock,
                )
                for item in items
            ]
            matches.append(
                ProductMatch(
                    title=product.title,
                    description=product.description,
                    category=product.category,
                    image_url=product.image_url,
                    items=item_matches,
                )
            )
        return SearchPage(matches=matches, offset=offset, limit=limit, has_more=has_more)
