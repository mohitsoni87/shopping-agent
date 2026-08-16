import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shopping_agent_common.config import get_common_settings
from shopping_agent_common.db.base import Base

if TYPE_CHECKING:
    from shopping_agent_common.db.models.item import Item

_embedding_dim = get_common_settings().embedding_dim


class Product(Base):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("tenant_id", "env", "external_product_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str]
    env: Mapped[str]
    external_product_id: Mapped[str]
    title: Mapped[str]
    description: Mapped[str]
    category: Mapped[str | None]
    image_url: Mapped[str | None]
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(_embedding_dim))
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    items: Mapped[list["Item"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
