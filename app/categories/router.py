from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from core.responses import CATEGORY_ALREADY_EXISTS, CATEGORY_NOT_FOUND
from . import service
from .schemas import CreateCategory, SetCategoryAttr
from ..auth.dependencies import db_dependency, get_current_admin

router = APIRouter(prefix="/categories", tags=["categories"])
admin_router = APIRouter(prefix="/admin/categories", tags=["admin-categories"],
                         dependencies=[Depends(get_current_admin)])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency):
    return await service.get_all_categories(db)


@router.get("/{category_id}", status_code=status.HTTP_200_OK, responses={**CATEGORY_NOT_FOUND})
async def get_category(db: db_dependency, category_id: int):
    result = await service.get_category_by_id(db, category_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return result


@admin_router.post("/", status_code=status.HTTP_201_CREATED,
                   responses={
                       **CATEGORY_ALREADY_EXISTS
                   })
async def create_category(db: db_dependency, create_data: CreateCategory):
    return await service.create_category(db, create_data)


@admin_router.put("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
                  responses={
                      **CATEGORY_ALREADY_EXISTS, **CATEGORY_NOT_FOUND
                  })
async def update_category(db: db_dependency, category_id: int, create_data: CreateCategory):
    return await service.update_category(db, category_id, create_data)


@admin_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
                     responses={**CATEGORY_NOT_FOUND})
async def delete_category(db: db_dependency, category_id: int):
    return await service.delete_category(db, category_id)


@admin_router.post("/attribute", status_code=status.HTTP_201_CREATED,
                   responses={**CATEGORY_NOT_FOUND})
async def set_attr(db: db_dependency, set_attr_data: SetCategoryAttr):
    return await service.set_category_attr(db, set_attr_data)


@admin_router.delete("/{category_id}/attribute/{attr_id}", status_code=status.HTTP_204_NO_CONTENT,
                     responses={**CATEGORY_NOT_FOUND})
async def delete_attr(db: db_dependency, category_id: int, attr_id: int):
    return await service.delete_category_attr(db, category_id, attr_id)


@admin_router.get("/{category_id}/attribute", status_code=status.HTTP_200_OK,
                  responses={**CATEGORY_NOT_FOUND})
async def get_attrs(db: db_dependency, category_id: int):
    return await service.get_category_attrs(db, category_id)
