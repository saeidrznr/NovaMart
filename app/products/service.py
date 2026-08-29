from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from database.models import Product, ProductImage
from .schemas import CreateProduct
from .storage.base import Storage

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def get_all_products(db: AsyncSession):
    result = await db.scalars(select(Product).options(selectinload(Product.images)))
    return result.all()


async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.scalar(select(Product).where(Product.id == product_id).options(selectinload(Product.images)))
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


async def upload_product_image(db: AsyncSession, storage: Storage, product_id: int, image: UploadFile,
                               is_primary: bool):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image type not allowed")

    extension = image.filename.rsplit(".", 1)[1]
    filename = f"{uuid4()}.{extension}"
    path = f"products/{product_id}/{filename}"

    image_url = await storage.upload(image, path)

    if is_primary:
        await db.execute(update(ProductImage).where(ProductImage.product_id == product_id).values(is_primary=False))

    product_image = ProductImage(product_id=product_id, image_url=image_url, is_primary=is_primary, path=path)

    db.add(product_image)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        await storage.delete(path)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save product image"
        )
    except Exception:
        await db.rollback()
        await storage.delete(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save product image"
        )


async def update_product_image(db: AsyncSession, storage: Storage, image_id: int, image: UploadFile, is_primary: bool):
    if image is None and is_primary is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")

    product_image: ProductImage | None = await db.scalar(select(ProductImage).where(ProductImage.id == image_id))
    if product_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if image and image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image type not allowed")

    old_path = None
    path = None
    if image is not None:
        old_path = product_image.path
        extension = image.filename.rsplit(".", 1)[1]
        filename = f"{uuid4()}.{extension}"
        path = f"products/{product_image.product_id}/{filename}"

        image_url = await storage.upload(image, path)
        product_image.image_url = image_url
        product_image.path = path

    if is_primary is not None:
        if is_primary:
            await db.execute(
                update(ProductImage).where(ProductImage.product_id == product_image.product_id,
                                           ProductImage.id != product_image.id).values(is_primary=False))

        product_image.is_primary = is_primary

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        if path:
            await storage.delete(path)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save product image"
        )
    except Exception:
        await db.rollback()
        if path:
            await storage.delete(path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save product image"
        )

    if old_path:
        await storage.delete(old_path)


async def delete_product_image(db: AsyncSession, storage: Storage, image_id: int):
    product_image: ProductImage | None = await db.scalar(select(ProductImage).where(ProductImage.id == image_id))
    if product_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product Image not found")

    await db.delete(product_image)
    await db.commit()

    await storage.delete(product_image.path)
