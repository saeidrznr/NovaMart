from fastapi import APIRouter, Path
from starlette import status

from core.responses import CART_IS_EMPTY, ORDER_NOT_FOUND
from . import service
from .schemas import OrderResponse, OrderValidationResponse
from ..auth.dependencies import db_dependency, user_id_dependency

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[OrderResponse])
async def get_orders(db: db_dependency, user_id: user_id_dependency):
    return await service.get_orders(db, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED, responses={
    **CART_IS_EMPTY
})
async def create_order(db: db_dependency, user_id: user_id_dependency):
    return await service.create_order(db, user_id)


@router.post("/{order_id}/validate-price", status_code=status.HTTP_200_OK, response_model=OrderValidationResponse,
             responses={
                 **ORDER_NOT_FOUND
             })
async def validate_price(db: db_dependency, user_id: user_id_dependency, order_id: int = Path(gt=0)):
    return await service.validate_price(db, user_id, order_id)


@router.post("/{order_id}/confirm", status_code=status.HTTP_204_NO_CONTENT
    , responses={
        **ORDER_NOT_FOUND
    })
async def confirm_price_changes(db: db_dependency, user_id: user_id_dependency, order_id: int = Path(gt=0)):
    return await service.confirm_price_changes(db, user_id, order_id)


@router.post("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, responses={**ORDER_NOT_FOUND})
async def cancel_order(db: db_dependency, user_id: user_id_dependency, order_id: int = Path(gt=0)):
    return await service.cancel_order(db, user_id, order_id)
