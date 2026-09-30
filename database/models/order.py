from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Enum as SqlEnum, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from order_item import OrderItem


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
