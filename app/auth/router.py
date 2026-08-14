from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.models.User import User
from .schemas import UserRegister
from .service import create_user, authenticate_user, get_refresh_token, refresh_session
from core.config import settings
from core.security import create_access_token
from database.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

        user_model = await db.scalar(select(User).where(User.id == user_id))
        if user_model is None:
            raise credentials_exception

    except (JWTError, ValueError):
        raise credentials_exception

    return user_model


db_dependency = Annotated[AsyncSession, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, user_register: UserRegister):
    await create_user(db, user_register)


@router.post("/login")
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


@router.get("/refresh")
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
