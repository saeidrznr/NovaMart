from pydantic import BaseModel, Field


class CreateCategory(BaseModel):
    name: str = Field(min_length=3, max_length=30)


class SetCategoryAttr(BaseModel):
    category_id: int = Field(gt=0)
    attribute_id: int = Field(gt=0)
