from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import CreateProduct
from database.models import Product


async def get_all_products(db: AsyncSession):
    result = await db.scalars(select(Product))
    return result.all()


async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.scalar(select(Product).where(Product.id == product_id))
    return result


async def create_product(db: AsyncSession, create_data: CreateProduct):
    product = Product(**create_data.model_dump())
    db.add(product)
    await db.commit()


async def update_product(db: AsyncSession, product_id: int, create_data: CreateProduct):
    result: Product | None = await db.scalar(select(Product).where(Product.id == product_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    result.name = create_data.name
    result.description = create_data.description
    result.is_active = create_data.is_active
    await db.commit()


async def delete_product(db: AsyncSession, product_id: int):
    result: Product | None = await db.scalar(select(Product).where(Product.id == product_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await db.delete(result)
    await db.commit()
