from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.attribute import Attribute
    from database.models.category import Category


class AttributeCategory(Base):
    __tablename__ = "attribute_category"
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), primary_key=True)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attribute.id", ondelete="CASCADE"), primary_key=True)

    category: Mapped["Category"] = relationship(back_populates="attribute_categories")
    attribute: Mapped["Attribute"] = relationship(back_populates="attribute_categories")
