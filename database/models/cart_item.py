from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.database import Base

if TYPE_CHECKING:
    from .cart import Cart
    from product_variant import ProductVariant


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
                      UniqueConstraint("cart_id", "variant_id", name="uq_cart_item_cart_variant"))

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="cascade"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variant.id", ondelete="cascade"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="items")

    variant: Mapped["ProductVariant"] = relationship(back_populates="cart_items")
