from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import CreateAttribute
from database.models import Attribute


async def get_all_attrs(db: AsyncSession):
    result = await db.scalars(select(Attribute))
    return result.all()


async def get_attr_by_id(db: AsyncSession, attr_id: int):
    result = await db.scalar(select(Attribute).where(Attribute.id == attr_id))
    return result


async def create_attr(db: AsyncSession, create_data: CreateAttribute):
    attr = Attribute(**create_data.model_dump())
    db.add(attr)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attribute already exists")


async def update_attr(db: AsyncSession, product_id: int, create_data: CreateAttribute):
    result: Attribute | None = await db.scalar(select(Attribute).where(Attribute.id == product_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    result.name = create_data.name
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attribute already exists")


async def delete_attr(db: AsyncSession, attr_id: int):
    result: Attribute | None = await db.scalar(select(Attribute).where(Attribute.id == attr_id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    await db.delete(result)
    await db.commit()
