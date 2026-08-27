from pydantic import BaseModel, Field


class CreateAttribute(BaseModel):
    name: str = Field(min_length=3, max_length=20)
