from decimal import Decimal

from pydantic import BaseModel, Field


# quantity_change can be less than 0
class CartItemQuantityChange(BaseModel):
    quantity_change: int


class CartItemQuantityUpdate(BaseModel):
    quantity: int = Field(gt=0)


class AttributeResponse(BaseModel):
    name: str
    value: str


class VariantResponse(BaseModel):
    id: int = Field(gt=0)
    price: Decimal
    name: str
    attributes: list[AttributeResponse]


class CartItemResponse(BaseModel):
    id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    variant: VariantResponse
    image_url: str | None = Field(default=None)
