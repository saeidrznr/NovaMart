from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .schemas import UserRegister
from core.config import settings
from core.security import hash_password, verify_password, create_refresh_token, hash_refresh_token
from database.models.refresh_session import RefreshSession
from database.models.user import User


async def create_user(db: AsyncSession, user_data: UserRegister):
    existing_user = await db.scalar(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username)))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or Username already exists")

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    await db.commit()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user_model: User | None = await db.scalar(select(User).where(User.username == username))
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not verify_password(password, user_model.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user_model


async def get_refresh_token(db: AsyncSession, user_id: int, expire_at: datetime):
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token)
    refresh_session = RefreshSession(user_id=user_id, token_hash=refresh_token_hash,
                                     expires_at=expire_at)

    db.add(refresh_session)
    await db.commit()

    return refresh_token


async def refresh_session(db: AsyncSession, refresh_token: str, expire_at: datetime):
    refresh_token_hash = hash_refresh_token(refresh_token)
    refresh_session_model: RefreshSession | None = await db.scalar(select(RefreshSession).where(
        (RefreshSession.token_hash == refresh_token_hash) & (RefreshSession.expires_at > datetime.now(timezone.utc)) & (
            RefreshSession.revoked.is_(False))))

    if refresh_session_model is None or refresh_session_model.created_at + timedelta(
            days=settings.REFRESH_TOKEN_ABSOLUTE_EXPIRE_DAYS) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    refresh_session_model.expires_at = expire_at

    db.add(refresh_session_model)
    await db.commit()
    return refresh_session_model.user_id
