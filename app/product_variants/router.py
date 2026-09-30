from fastapi import APIRouter, Depends
from starlette import status

from core.responses import PRODUCT_NOT_FOUND, DUPLICATE_ATTRIBUTES, VARIANT_NOT_FOUND
from ..auth.dependencies import get_current_admin, db_dependency
from .schemas import CreateProductVariant, UpdateProductVariant, VariantResponse
from . import service

router = APIRouter(prefix="/variants", tags=["variants"])
admin_router = APIRouter(prefix="/admin/variants", tags=["admin-variants"], dependencies=[Depends(get_current_admin)])


@router.get("/product/{product_id}", responses={**PRODUCT_NOT_FOUND}, response_model=list[VariantResponse],
            response_model_exclude_none=True)
async def get_product_variants(db: db_dependency, product_id: int):
    return await service.get_product_variants(db, product_id)


@admin_router.get("/product/{product_id}", responses={**PRODUCT_NOT_FOUND}, response_model=list[VariantResponse],
                  response_model_exclude_none=True)
async def get_product_variants(db: db_dependency, product_id: int):
    return await service.get_product_variants_for_admin(db, product_id)


@admin_router.post("/product/{product_id}", status_code=status.HTTP_201_CREATED,
                   responses={
                       **PRODUCT_NOT_FOUND, **DUPLICATE_ATTRIBUTES
                   })
async def create_variant(db: db_dependency, product_id: int, create_data: CreateProductVariant):
    return await service.create_variant(db, product_id, create_data)


@admin_router.put("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT,
                  responses={
                      **VARIANT_NOT_FOUND, **DUPLICATE_ATTRIBUTES
                  })
async def update_variant(db: db_dependency, variant_id: int, update_data: UpdateProductVariant):
    return await service.update_variant(db, variant_id, update_data)


@admin_router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT,
                     responses={
                         **VARIANT_NOT_FOUND
                     })
async def delete_variant(db: db_dependency, variant_id: int):
    return await service.delete_variant(db, variant_id)
