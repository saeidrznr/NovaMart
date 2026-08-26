from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.attribute_category import AttributeCategory
    from database.models.variant_attribute import VariantAttribute


class Attribute(Base):
    __tablename__ = "attribute"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    attribute_categories: Mapped[list["AttributeCategory"]] = relationship(back_populates="attribute",
                                                                           cascade="all, delete-orphan")
    variant_attributes: Mapped[list["VariantAttribute"]] = relationship(back_populates="attribute",
                                                                        cascade="all, delete-orphan")
