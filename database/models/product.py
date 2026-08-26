from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.category import Category
    from database.models.product_image import ProductImage
    from database.models.product_variant import ProductVariant


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product", cascade="all, delete-orphan")
