from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from core.responses import ATTRIBUTE_NOT_FOUND, ATTRIBUTE_ALREADY_EXISTS
from . import service
from .schemas import CreateAttribute
from ..auth.dependencies import db_dependency, get_current_admin

router = APIRouter(prefix="/attributes", tags=["admin-attributes"])


@router.get("/", status_code=status.HTTP_200_OK, tags=["attributes"])
async def get_attrs(db: db_dependency):
    return await service.get_all_attrs(db)


@router.get("/{attr_id}", status_code=status.HTTP_200_OK, responses={**ATTRIBUTE_NOT_FOUND}, tags=["attributes"])
async def get_attr(db: db_dependency, attr_id: int):
    result = await service.get_attr_by_id(db, attr_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    return result


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_admin)],
             responses={**ATTRIBUTE_ALREADY_EXISTS})
async def create_attr(db: db_dependency, create_data: CreateAttribute):
    return await service.create_attr(db, create_data)


@router.put("/{attr_id}", status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_current_admin)], responses={
        **ATTRIBUTE_NOT_FOUND, **ATTRIBUTE_ALREADY_EXISTS
    })
async def update_attr(db: db_dependency, attr_id: int, create_data: CreateAttribute):
    return await service.update_attr(db, attr_id, create_data)


@router.delete("/{attr_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)], responses={**ATTRIBUTE_NOT_FOUND})
async def delete_attr(db: db_dependency, attr_id: int):
    return await service.delete_attr(db, attr_id)
