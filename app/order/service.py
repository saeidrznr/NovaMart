from decimal import Decimal
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from database.models import Cart, CartItem, ProductVariant, VariantAttribute, Attribute, Product
from database.models import Order, OrderItem
from database.models.order import OrderStatus
from .schemas import OrderItemResponse, VariantResponse, AttributeResponse, OrderResponse, OrderItemChangeResponse, \
    OrderValidationResponse


async def get_orders(db: AsyncSession, user_id: int):
    orders = (await db.scalars(select(Order)
    .where(Order.user_id == user_id)
    .options(
        selectinload(Order.items).load_only(OrderItem.quantity, OrderItem.unit_price).selectinload(
            OrderItem.variant).options(selectinload(
            ProductVariant.product).load_only(
            Product.name,
        ).selectinload(Product.images),
                                       selectinload(
                                           ProductVariant.attributes).load_only(
                                           VariantAttribute.value).selectinload(
                                           VariantAttribute.attribute).load_only(Attribute.name)
                                       )
    ))).all()

    result = []
    for order in orders:
        order_response = OrderResponse(status=order.status, total_price=order.total_price, id=order.id,
                                       created_at=order.created_at, updated_at=order.updated_at, items=[])

        for item in order.items:
            order_item = OrderItemResponse(id=item.id, quantity=item.quantity, order_price=item.unit_price, variant=
            VariantResponse(id=item.variant.id, price=item.variant.price, name=item.variant.product.name,
                            attributes=[AttributeResponse(name=attr.attribute.name, value=attr.value) for attr in
                                        item.variant.attributes]))
            if item.variant.product.images:
                image_url = item.variant.product.images[0].image_url
                for image in item.variant.product.images:
                    if image.is_primary:
                        image_url = image.image_url
                        break
                order_item.image_url = image_url
            order_response.items.append(order_item)

        result.append(order_response)
    return result


async def create_order(db: AsyncSession, user_id: int):
    cart: Cart | None = await db.scalar(select(Cart).where(Cart.user_id == user_id))
    if cart is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    cart_items = (
        await db.scalars(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(
                selectinload(CartItem.variant)
            )
        )
    ).all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    try:
        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_price=Decimal("0")
        )
        db.add(order)
        await db.flush()

        total_price = Decimal("0")

        for cart_item in cart_items:
            unit_price = cart_item.variant.price

            order_item = OrderItem(
                order_id=order.id,
                variant_id=cart_item.variant_id,
                quantity=cart_item.quantity,
                unit_price=unit_price
            )

            db.add(order_item)
            total_price += unit_price * cart_item.quantity

        order.total_price = total_price

        for cart_item in cart_items:
            await db.delete(cart_item)

        await db.commit()

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def _get_order_with_items_and_variants(db: AsyncSession, order_id: int, user_id: int):
    order: Order | None = await db.scalar(
        select(Order).where(Order.id == order_id, Order.user_id == user_id).options(selectinload(Order.items)))
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    variants_id = [item.variant_id for item in order.items]

    variants: Sequence[ProductVariant] = (
        await db.scalars(select(ProductVariant).where(ProductVariant.id.in_(variants_id)).options(
            selectinload(ProductVariant.product).load_only(Product.name)))).all()

    return order, variants


async def validate_price(db: AsyncSession, user_id: int, order_id: int):
    order, variants = await _get_order_with_items_and_variants(db, order_id, user_id)

    variants_by_id = {variant.id: variant for variant in variants}
    changes = []
    for item in order.items:
        variant = variants_by_id[item.variant_id]
        if item.unit_price != variant.price:
            change = OrderItemChangeResponse(id=item.id, name=variant.product.name, old_price=item.unit_price,
                                             current_price=variant.price)
            changes.append(change)

    return OrderValidationResponse(valid=not changes, changes=changes)


# confirm new prices that means update order item's prices to current prices
async def confirm_price_changes(db: AsyncSession, user_id: int, order_id: int):
    order, variants = await _get_order_with_items_and_variants(db, order_id, user_id)

    variants_by_id = {variant.id: variant for variant in variants}
    for item in order.items:
        variant = variants_by_id[item.variant_id]
        if item.unit_price != variant.price:
            order.total_price += (variant.price - item.unit_price) * item.quantity
            item.unit_price = variant.price

    await db.commit()


async def cancel_order(db: AsyncSession, user_id: int, order_id: int):
    order: Order | None = await db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user_id,
                                                              Order.status.in_(
                                                                  [OrderStatus.PENDING, OrderStatus.PAID])))
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = OrderStatus.CANCELLED
    await db.commit()
