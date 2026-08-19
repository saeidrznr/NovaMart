from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from .dependencies import db_dependency
from .schemas import UserRegister
from .service import create_user, authenticate_user, get_refresh_token, refresh_session
from core.config import settings
from core.security import create_access_token

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=status.HTTP_201_CREATED,tags=["user"])
async def register_user(db: db_dependency, user_register: UserRegister):
    await create_user(db, user_register)


@router.post("/login",tags=["user","admin"])
async def login_user(response: Response, db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form_data.username, form_data.password)

    refresh_token_expire_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_IDLE_EXPIRE_DAYS)

    refresh_token = await get_refresh_token(db, user.id, refresh_token_expire_at)

    access_token_timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)},
                                       expires_delta=access_token_timedelta)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax",
                        secure=settings.COOKIE_SECURE)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/refresh",tags=["user","admin"])
async def refresh_access_token(db: db_dependency,
                               refresh_token: Annotated[str | None, Cookie()]):
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token not provided")

    refresh_token_expire_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_IDLE_EXPIRE_DAYS)

    user_id = await refresh_session(db, refresh_token, refresh_token_expire_at)
    access_token_timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": user_id},
                                       expires_delta=access_token_timedelta)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
