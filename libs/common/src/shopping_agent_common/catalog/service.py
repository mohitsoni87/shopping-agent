from datetime import UTC, datetime

from sqlalchemy.orm import Session

from shopping_agent_common.catalog.schemas import ProductUpsert
from shopping_agent_common.db.models import Item, Product
from shopping_agent_common.embeddings import EmbeddingClient
from shopping_agent_common.repositories import ItemRepository, ProductRepository


class CatalogService:
    """Owns the write path for the Feature Store: upserting a product and its
    items, keeping the embedding in sync with the product's text. Used by both
    the ingestion webhook and the catalog seed script.
    """

    def __init__(self, session: Session, embedding_client: EmbeddingClient):
        self._products = ProductRepository(session)
        self._items = ItemRepository(session)
        self._embeddings = embedding_client

    def upsert_product(self, tenant_id: str, env: str, payload: ProductUpsert) -> Product:
        embedding_text = f"{payload.title}\n{payload.description}"
        [embedding] = self._embeddings.embed_documents([embedding_text])

        now = datetime.now(UTC)

        product = self._products.get_by_external_id(tenant_id, env, payload.external_product_id)
        if product is None:
            product = Product(
                tenant_id=tenant_id,
                env=env,
                external_product_id=payload.external_product_id,
                created_at=now,
            )
            self._products.add(product)

        product.title = payload.title
        product.description = payload.description
        product.category = payload.category
        product.image_url = payload.image_url
        product.attributes = payload.attributes
        product.embedding = embedding
        product.updated_at = now

        self._products.flush()

        for item_payload in payload.items:
            item = self._items.get_by_external_id(tenant_id, env, item_payload.external_item_id)
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
        return product
