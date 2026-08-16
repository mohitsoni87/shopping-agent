import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shopping_agent_common.db.base import Base

if TYPE_CHECKING:
    from shopping_agent_common.db.models.product import Product


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (UniqueConstraint("tenant_id", "env", "external_item_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    tenant_id: Mapped[str]
    env: Mapped[str]
    external_item_id: Mapped[str]
    size: Mapped[str | None]
    color: Mapped[str | None]
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    product: Mapped["Product"] = relationship(back_populates="items")
