from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, load_only
from starlette import status

from database.models import Cart, CartItem, ProductVariant, VariantAttribute, Attribute, Product
from .schemas import CartItemQuantityChange, CartItemQuantityUpdate, CartItemResponse, VariantResponse, \
    AttributeResponse


async def get_cart(db: AsyncSession, user_id: int):
    cart_items = (await db.scalars(
        select(CartItem).join(CartItem.cart).where(Cart.user_id == user_id).options(load_only(CartItem.quantity),
                                                                                    selectinload(
                                                                                        CartItem.variant).load_only(
                                                                                        ProductVariant.price).options(
                                                                                        selectinload(
                                                                                            ProductVariant.product).load_only(
                                                                                            Product.name,
                                                                                        ).selectinload(Product.images),
                                                                                        selectinload(
                                                                                            ProductVariant.attributes).load_only(
                                                                                            VariantAttribute.value).selectinload(
                                                                                            VariantAttribute.attribute).load_only(

                                                                                            Attribute.name))))).all()

    result = []
    for item in cart_items:
        cart_item = CartItemResponse(id=item.id, quantity=item.quantity, variant=
        VariantResponse(id=item.variant.id, price=item.variant.price, name=item.variant.product.name,
                        attributes=[AttributeResponse(name=attr.attribute.name, value=attr.value) for attr in
                                    item.variant.attributes]))
        if item.variant.product.images:
            image_url = item.variant.product.images[0].image_url
            for image in item.variant.product.images:
                if image.is_primary:
                    image_url = image.image_url
                    break
            cart_item.image_url = image_url
        result.append(cart_item)
    return result


async def item_quantity_change(db: AsyncSession, user_id: int, variant_id: int,
                               change_quantity_data: CartItemQuantityChange):
    cart_item: CartItem | None = await db.scalar(
        select(CartItem).join(CartItem.cart).where(CartItem.variant_id == variant_id,
                                                   Cart.user_id == user_id))
    if cart_item is None:
        variant: ProductVariant | None = await db.scalar(select(ProductVariant).where(ProductVariant.id == variant_id))
        if variant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production Variant not found")

        if change_quantity_data.quantity_change <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")

        cart: Cart | None = await db.scalar(select(Cart).where(Cart.user_id == user_id))
        if cart is None:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.flush()
        cart_item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=change_quantity_data.quantity_change)
        db.add(cart_item)
    else:
        if cart_item.quantity + change_quantity_data.quantity_change <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive")

        cart_item.quantity += change_quantity_data.quantity_change

    await db.commit()


async def update_cart_item(db: AsyncSession, user_id, item_id, update_data: CartItemQuantityUpdate):
    cart_item: CartItem | None = await db.scalar(
        select(CartItem).join(CartItem.cart).where(CartItem.id == item_id, Cart.user_id == user_id))
    if cart_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart Item not found")

    cart_item.quantity = update_data.quantity
    await db.commit()


async def delete_cart_item(db: AsyncSession, user_id: int, item_id: int):
    cart_item: CartItem | None = await db.scalar(
        select(CartItem).join(CartItem.cart).where(CartItem.id == item_id, Cart.user_id == user_id))
    if cart_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart Item not found")

    await db.delete(cart_item)
    await db.commit()
