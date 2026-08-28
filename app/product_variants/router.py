from fastapi import APIRouter, Depends
from starlette import status

from core.responses import PRODUCT_NOT_FOUND, DUPLICATE_ATTRIBUTES, VARIANT_NOT_FOUND
from ..auth.dependencies import get_current_admin, db_dependency
from .schemas import CreateProductVariant, UpdateProductVariant
from . import service

router = APIRouter(prefix="/variants", tags=["admin-variants"])


@router.get("/product/{product_id}", responses={**PRODUCT_NOT_FOUND}, tags=["variants"])
async def get_product_variants(db: db_dependency, product_id: int):
    return await service.get_product_variants(db, product_id)


@router.post("/product/{product_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin)],
             responses={
                 **PRODUCT_NOT_FOUND, **DUPLICATE_ATTRIBUTES
             })
async def create_variant(db: db_dependency, product_id: int, create_data: CreateProductVariant):
    return await service.create_variant(db, product_id, create_data)


@router.put("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)],
            responses={
                **VARIANT_NOT_FOUND, **DUPLICATE_ATTRIBUTES
            })
async def update_variant(db: db_dependency, variant_id: int, update_data: UpdateProductVariant):
    return await service.update_variant(db, variant_id, update_data)


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)],
               responses={
                   **VARIANT_NOT_FOUND
               })
async def delete_variant(db: db_dependency, variant_id: int):
    return await service.delete_variant(db, variant_id)
