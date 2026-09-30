from fastapi import APIRouter, Path
from starlette import status

from core.responses import VARIANT_NOT_FOUND, QUANTITY_MUST_BE_POSITIVE, CART_ITEM_NOT_FOUND
from . import service
from .schemas import CartItemQuantityUpdate, CartItemQuantityChange, CartItemResponse
from ..auth.dependencies import db_dependency, user_id_dependency

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[CartItemResponse])
async def get_cart(db: db_dependency, user_id: user_id_dependency):
    return await service.get_cart(db, user_id)


@router.post("/items/{variant_id}", status_code=status.HTTP_201_CREATED, responses={
    **VARIANT_NOT_FOUND, **QUANTITY_MUST_BE_POSITIVE
})
async def item_quantity_change(db: db_dependency, change_quantity_data: CartItemQuantityChange,
                               user_id: user_id_dependency
                               , variant_id: int = Path(gt=0)):
    return await service.item_quantity_change(db, user_id, variant_id, change_quantity_data)


@router.patch("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
              responses={
                  **CART_ITEM_NOT_FOUND
              })
async def update_cart_item(db: db_dependency, user_id: user_id_dependency, item_id: int, update_data: CartItemQuantityUpdate):
    return await service.update_cart_item(db, user_id, item_id, update_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, responses={**CART_ITEM_NOT_FOUND})
async def delete_product(db: db_dependency, user_id: user_id_dependency, item_id: int = Path(gt=0)):
    return await service.delete_cart_item(db, user_id, item_id)
