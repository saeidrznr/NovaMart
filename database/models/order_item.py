from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from database.database import Base
if TYPE_CHECKING:
    from .order import Order
    from .product_variant import ProductVariant

class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variant.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    order: Mapped["Order"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="order_items")
