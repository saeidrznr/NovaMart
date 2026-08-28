from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from database.models import Product, AttributeCategory, ProductVariant, VariantAttribute
from .schemas import CreateProductVariant, UpdateProductVariant


async def get_product_variants(db: AsyncSession, product_id: int):
    product: Product | None = await db.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    result = await db.scalars(select(ProductVariant).where(ProductVariant.product_id == product_id).options(
        selectinload(ProductVariant.attributes)))
    return result.all()


async def create_variant(db: AsyncSession, product_id: int, create_data: CreateProductVariant):
    product: Product | None = await db.scalar(select(Product).where(Product.id == product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    allowed_attributes_ids = set(await db.scalars(
        select(AttributeCategory.attribute_id).where(AttributeCategory.category_id == product.category_id)))

    attribute_ids = [attr.attribute_id for attr in create_data.attributes]

    if len(attribute_ids) != len(set(attribute_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate attributes are not allowed")

    if len(attribute_ids) < len(allowed_attributes_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must send all attributes")

    invalid_attributes = (set(attribute_ids) - allowed_attributes_ids)

    if invalid_attributes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid attributes: {invalid_attributes}")

    variant = ProductVariant(product_id=product_id, sku=create_data.sku, price=create_data.price,
                             stock=create_data.stock, is_active=create_data.is_active)

    # Create transaction
    db.add(variant)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Variant already exists")

    for attr in create_data.attributes:
        variant_attribute = VariantAttribute(variant_id=variant.id, attribute_id=attr.attribute_id, value=attr.value)
        db.add(variant_attribute)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Variant already exists")


async def update_variant(db: AsyncSession, variant_id: int, update_data: UpdateProductVariant):
    if not update_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    variant: ProductVariant | None = await db.scalar(select(ProductVariant).where(ProductVariant.id == variant_id))
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    if update_data.attributes is not None:
        allowed_attributes = (await db.scalars(
            select(VariantAttribute).where(VariantAttribute.variant_id == variant_id))).all()

        allowed_attributes_ids = {
            attr.attribute_id
            for attr in allowed_attributes
        }

        attribute_ids = [attr.attribute_id for attr in update_data.attributes]

        if len(attribute_ids) != len(set(attribute_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate attributes are not allowed")

        invalid_attributes = (set(attribute_ids) - allowed_attributes_ids)

        if invalid_attributes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid attributes: {invalid_attributes}")

        variant_attributes = {item.attribute_id: item for item in allowed_attributes}
        for attr in update_data.attributes:
            variant_attribute = variant_attributes.get(attr.attribute_id)
            variant_attribute.value = attr.value

    if update_data.sku is not None:
        variant.sku = update_data.sku

    if update_data.price is not None:
        variant.price = update_data.price

    if update_data.stock is not None:
        variant.stock = update_data.stock

    if update_data.is_active is not None:
        variant.is_active = update_data.is_active

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Variant already exists")


async def delete_variant(db: AsyncSession, variant_id: int):
    variant: ProductVariant | None = await db.scalar(select(ProductVariant).where(ProductVariant.id == variant_id))
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    await db.delete(variant)
    await db.commit()
