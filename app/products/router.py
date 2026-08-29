from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from starlette import status

from core.responses import PRODUCT_NOT_FOUND, INTERNAL_SERVER_ERROR, IMAGE_NOT_FOUND, NOTHING_TO_UPDATE, \
    PRODUCT_IMAGE_NOT_FOUND
from . import service
from .dependencies import get_storage
from .schemas import CreateProduct
from .storage.base import Storage
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


@router.post("/{product_id}/images", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin)],
             responses={**PRODUCT_NOT_FOUND, **INTERNAL_SERVER_ERROR})
async def upload_product_image(db: db_dependency, product_id: int, image: UploadFile = File(...),
                               is_primary: bool = Form(False), storage: Storage = Depends(get_storage)):
    return await service.upload_product_image(
        db,
        storage,
        product_id,
        image,
        is_primary
    )


@router.put("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_admin)],
            responses={**IMAGE_NOT_FOUND, **INTERNAL_SERVER_ERROR, **NOTHING_TO_UPDATE})
async def update_product_image(db: db_dependency, image_id: int, image: UploadFile = File(default=None),
                               is_primary: bool = Form(default=None), storage: Storage = Depends(get_storage)):
    return await service.update_product_image(db, storage, image_id, image, is_primary)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(get_current_admin)],responses={
    **PRODUCT_IMAGE_NOT_FOUND
})
async def delete_product_image(db: db_dependency,image_id: int,storage:Storage=Depends(get_storage)):
    return await service.delete_product_image(db, storage, image_id)