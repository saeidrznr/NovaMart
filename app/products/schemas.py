from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    category_id: int = Field(gt=0)
    description: str = Field(min_length=3, max_length=1000)
    is_active: bool
