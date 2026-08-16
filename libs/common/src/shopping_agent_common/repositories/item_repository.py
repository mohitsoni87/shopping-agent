import uuid
from dataclasses import dataclass

from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import Session

from shopping_agent_common.db.models import Item, Product


@dataclass(frozen=True, slots=True)
class ItemFilters:
    size: str | None = None
    color: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    in_stock_only: bool = True


class ItemRepository:
    def __init__(self, session: Session):
        self._session = session

    def _conditions(
        self, tenant_id: str, env: str, filters: ItemFilters
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = [Item.tenant_id == tenant_id, Item.env == env]
        if filters.size:
            conditions.append(Item.size == filters.size)
        if filters.color:
            conditions.append(Item.color == filters.color)
        if filters.price_min is not None:
            conditions.append(Item.price >= filters.price_min)
        if filters.price_max is not None:
            conditions.append(Item.price <= filters.price_max)
        if filters.in_stock_only:
            conditions.append(Item.stock > 0)
        return conditions

    def exists_for_product(self, tenant_id: str, env: str, filters: ItemFilters):
        """Correlated EXISTS clause; must be used inside a Product query so
        `Item.product_id == Product.id` correlates against the outer FROM."""
        conditions = self._conditions(tenant_id, env, filters)
        return select(Item.id).where(Item.product_id == Product.id, *conditions).exists()

    def list_for_product(
        self, product_id: uuid.UUID, tenant_id: str, env: str, filters: ItemFilters
    ) -> list[Item]:
        conditions = self._conditions(tenant_id, env, filters)
        stmt = select(Item).where(Item.product_id == product_id, *conditions)
        return list(self._session.execute(stmt).scalars().all())

    def get_by_external_id(self, tenant_id: str, env: str, external_item_id: str) -> Item | None:
        stmt = select(Item).where(
            Item.tenant_id == tenant_id,
            Item.env == env,
            Item.external_item_id == external_item_id,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def add(self, item: Item) -> None:
        self._session.add(item)
