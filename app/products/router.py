from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from core.responses import PRODUCT_NOT_FOUND
from . import service
from .schemas import CreateProduct
from ..auth.dependencies import db_dependency, get_current_admin

router = APIRouter(prefix="/products", tags=["admin-products"])


@router.get("/", status_code=status.HTTP_200_OK, tags=["products"])
async def get_products(db: db_dependency):
    return await service.get_all_products(db)


@router.get("/{product_id}", status_code=status.HTTP_200_OK, responses={**PRODUCT_NOT_FOUND}, tags=["products"])
async def get_product(db: db_dependency, product_id: int):
    result = await service.get_product_by_id(db, product_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return result


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin)])
async def create_product(db: db_dependency, create_data: CreateProduct):
    return await service.create_product(db, create_data)


@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_current_admin)], responses={
        **PRODUCT_NOT_FOUND
    })
async def update_product(db: db_dependency, product_id: int, create_data: CreateProduct):
    return await service.update_product(db, product_id, create_data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)], responses={**PRODUCT_NOT_FOUND})
async def delete_product(db: db_dependency, product_id: int):
    return await service.delete_product(db, product_id)
