from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import CreateCategory
from database.models import Category


async def get_all_categories(db: AsyncSession):
    result = await db.scalars(select(Category))
    return result.all()


async def get_category_by_id(db: AsyncSession, category_id: int):
    result = await db.scalar(select(Category).where(Category.id == category_id))
    return result


async def create_category(db: AsyncSession, create_data: CreateCategory):
    category = Category(**create_data.model_dump())
    db.add(category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")


async def update_category(db: AsyncSession, category_id: int, create_data: CreateCategory):
    result: Category | None = await db.scalar(select(Category).where(Category.id == category_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    result.name = create_data.name
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")


async def delete_category(db: AsyncSession, category_id: int):
    result: Category | None = await db.scalar(select(Category).where(Category.id == category_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.delete(result)
    await db.commit()

