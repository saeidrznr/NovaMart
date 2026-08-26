from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.product import Product
    from database.models.variant_attribute import VariantAttribute


class ProductVariant(Base):
    __tablename__ = "product_variant"
    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="variants")
    attributes: Mapped[list["VariantAttribute"]] = relationship(back_populates="variant", cascade="all, delete-orphan")
