from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.product_variant import ProductVariant
    from database.models.attribute import Attribute


class VariantAttribute(Base):
    __tablename__ = "variant_attribute"
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variant.id", ondelete="cascade"), primary_key=True)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("attribute.id", ondelete="cascade"), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    variant: Mapped["ProductVariant"] = relationship(back_populates="attributes")
    attribute: Mapped["Attribute"] = relationship(back_populates="variant_attributes")
