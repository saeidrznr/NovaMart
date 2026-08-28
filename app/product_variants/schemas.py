from decimal import Decimal

from pydantic import BaseModel, Field


class VariantAttributeCreate(BaseModel):
    attribute_id: int = Field(gt=0)
    value: str = Field(min_length=1, max_length=100)


class CreateProductVariant(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    attributes: list[VariantAttributeCreate] = Field(min_length=1)
    is_active: bool


class UpdateProductVariant(BaseModel):
    sku: str | None = Field(min_length=1, max_length=100, default=None)
    price: Decimal | None = Field(gt=0, default=None)
    stock: int | None = Field(ge=0, default=None)
    attributes: list[VariantAttributeCreate] | None = Field(min_length=1, default=None)
    is_active: bool | None = Field(default=None)
