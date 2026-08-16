import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from shopping_agent_common.catalog.schemas import ItemUpsert, ProductUpsert, UpsertOutcome
from shopping_agent_common.db.models import Item, Product
from shopping_agent_common.embeddings import EmbeddingClient
from shopping_agent_common.repositories import ItemRepository, ProductRepository

logger = logging.getLogger(__name__)


def _prices_equal(db_price: Decimal | None, payload_price: float | None) -> bool:
    if db_price is None or payload_price is None:
        return db_price is None and payload_price is None
    # Compare via str() (not a bare float->Decimal cast) to avoid binary
    # float imprecision reporting a false "changed" for ordinary prices
    # like 19.99.
    return db_price == Decimal(str(payload_price))


def _product_content_changed(product: Product, payload: ProductUpsert) -> bool:
    """True if the fields that feed the embedding (title/description)
    differ - the only case that justifies a new, costly Voyage call."""
    return product.title != payload.title or product.description != payload.description


def _product_fields_changed(product: Product, payload: ProductUpsert) -> bool:
    return (
        _product_content_changed(product, payload)
        or product.category != payload.category
        or product.gender != payload.gender
        or product.image_url != payload.image_url
        or product.attributes != payload.attributes
    )


def _item_fields_changed(item: Item, payload: ItemUpsert) -> bool:
    return (
        item.size != payload.size
        or item.color != payload.color
        or not _prices_equal(item.price, payload.price)
        or item.stock != payload.stock
    )


class CatalogService:
    """Owns the write path for the Feature Store: upserting a product and its
    items, keeping the embedding in sync with the product's text. Used by both
    the ingestion webhook and the catalog seed CLI.
    """

    def __init__(self, session: Session, embedding_client: EmbeddingClient):
        self._products = ProductRepository(session)
        self._items = ItemRepository(session)
        self._embeddings = embedding_client

    def upsert_product(
        self, tenant_id: str, env: str, payload: ProductUpsert
    ) -> tuple[Product, UpsertOutcome]:
        now = datetime.now(UTC)

        product = self._products.get_by_external_id(tenant_id, env, payload.external_product_id)
        is_new_product = product is None
        if is_new_product:
            product = Product(
                tenant_id=tenant_id,
                env=env,
                external_product_id=payload.external_product_id,
                created_at=now,
            )

        existing_items = {
            item_payload.external_item_id: self._items.get_by_external_id(
                tenant_id, env, item_payload.external_item_id
            )
            for item_payload in payload.items
        }

        product_changed = is_new_product or _product_fields_changed(product, payload)
        items_changed = any(
            existing_items[ip.external_item_id] is None
            or _item_fields_changed(existing_items[ip.external_item_id], ip)
            for ip in payload.items
        )

        if not product_changed and not items_changed:
            logger.info(
                "catalog.upsert external_product_id=%s tenant_id=%s env=%s outcome=unchanged",
                payload.external_product_id,
                tenant_id,
                env,
            )
            return product, UpsertOutcome.UNCHANGED

        needs_embedding = is_new_product or _product_content_changed(product, payload)
        if needs_embedding:
            embedding_text = f"{payload.title}\n{payload.description}"
            [embedding] = self._embeddings.embed_documents([embedding_text])
        else:
            embedding = product.embedding

        if is_new_product:
            self._products.add(product)

        product.title = payload.title
        product.description = payload.description
        product.category = payload.category
        product.gender = payload.gender
        product.image_url = payload.image_url
        product.attributes = payload.attributes
        product.embedding = embedding
        product.updated_at = now

        self._products.flush()

        for item_payload in payload.items:
            item = existing_items[item_payload.external_item_id]
            if item is None:
                item = Item(
                    product_id=product.id,
                    tenant_id=tenant_id,
                    env=env,
                    external_item_id=item_payload.external_item_id,
                    created_at=now,
                )
                self._items.add(item)

            item.product_id = product.id
            item.size = item_payload.size
            item.color = item_payload.color
            item.price = item_payload.price
            item.stock = item_payload.stock
            item.updated_at = now

        self._products.flush()

        outcome = UpsertOutcome.CREATED if is_new_product else UpsertOutcome.UPDATED
        logger.info(
            "catalog.upsert external_product_id=%s tenant_id=%s env=%s outcome=%s embedding=%s",
            payload.external_product_id,
            tenant_id,
            env,
            outcome.value,
            "regenerated" if needs_embedding else "reused",
        )
        return product, outcome
