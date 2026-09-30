from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from database.models.order import OrderStatus


class AttributeResponse(BaseModel):
    name: str
    value: str


class VariantResponse(BaseModel):
    id: int = Field(gt=0)
    price: Decimal
    name: str
    attributes: list[AttributeResponse]


class OrderItemResponse(BaseModel):
    id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    variant: VariantResponse
    order_price: Decimal
    image_url: str | None = Field(default=None)


class OrderItemChangeResponse(BaseModel):
    id: int = Field(gt=0)
    name: str
    old_price: Decimal
    current_price: Decimal


class OrderResponse(BaseModel):
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    id: int = Field(gt=0)
    total_price: Decimal
    items: list[OrderItemResponse]


class OrderValidationResponse(BaseModel):
    valid: bool
    changes: list[OrderItemChangeResponse]
