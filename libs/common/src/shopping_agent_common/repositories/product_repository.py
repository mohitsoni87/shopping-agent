from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import Session

from shopping_agent_common.db.models import Product


class ProductRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_external_id(
        self, tenant_id: str, env: str, external_product_id: str
    ) -> Product | None:
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.env == env,
            Product.external_product_id == external_product_id,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def add(self, product: Product) -> None:
        self._session.add(product)

    def flush(self) -> None:
        self._session.flush()

    def list_categories(self, tenant_id: str, env: str) -> list[str]:
        stmt = (
            select(Product.category)
            .where(
                Product.tenant_id == tenant_id,
                Product.env == env,
                Product.category.is_not(None),
            )
            .distinct()
        )
        return [c for c in self._session.execute(stmt).scalars().all() if c]

    def search_by_similarity(
        self,
        *,
        tenant_id: str,
        env: str,
        query_embedding: list[float],
        category: str | None,
        has_matching_item: ColumnElement[bool],
        limit: int,
        offset: int = 0,
    ) -> list[Product]:
        """Returns up to `limit` products ordered by vector distance, starting
        at `offset`. Ordering must stay stable across pages: always the same
        `ORDER BY distance` with no secondary tiebreaker needed, since cosine
        distance over a fixed embedding is deterministic per product."""
        distance = Product.embedding.cosine_distance(query_embedding)
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.env == env,
            has_matching_item,
        )
        if category:
            stmt = stmt.where(Product.category == category)
        stmt = stmt.order_by(distance).offset(offset).limit(limit)
        return list(self._session.execute(stmt).scalars().all())
