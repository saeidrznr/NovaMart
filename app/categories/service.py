from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import CreateCategory, SetCategoryAttr
from database.models import Category, Attribute, AttributeCategory


async def get_all_categories(db: AsyncSession):
    result = await db.scalars(select(Category))
    return result.all()


async def get_category_by_id(db: AsyncSession, category_id: int):
    result = await db.scalar(select(Category).where(Category.id == category_id))
    return result


async def get_attribute_by_id(db: AsyncSession, attribute_id: int):
    result = await db.scalar(select(Attribute).where(Attribute.id == attribute_id))
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


async def set_category_attr(db: AsyncSession, set_attr_data: SetCategoryAttr):
    if await get_category_by_id(db, set_attr_data.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if await get_attribute_by_id(db, set_attr_data.attribute_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    attr_category = AttributeCategory(**set_attr_data.model_dump())
    db.add(attr_category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This Attribute already set to This Category")


async def get_category_attrs(db: AsyncSession, category_id: int):
    category_result = await db.scalar(select(Category).where(Category.id == category_id))
    if category_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    result = await db.scalars(
        select(Attribute).join(AttributeCategory).where(AttributeCategory.category_id == category_id))

    return result.all()


async def delete_category_attr(db: AsyncSession, category_id: int, attribute_id: int):
    if await get_category_by_id(db, category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if await get_attribute_by_id(db, attribute_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    result = await db.scalar(select(AttributeCategory).where(AttributeCategory.attribute_id == attribute_id,
                                                             AttributeCategory.category_id == category_id))

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No relation between given category and attribute")

    await db.delete(result)
    await db.commit()
