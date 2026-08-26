from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, relationship, Mapped
from database.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.product import Product
    from database.models.attribute_category import AttributeCategory


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                       nullable=False)
    products: Mapped[list["Product"]] = relationship(back_populates="category")
    attribute_categories: Mapped[list["AttributeCategory"]] = relationship(back_populates="category", cascade= "all, delete-orphan")
