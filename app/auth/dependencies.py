from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import or_

from core.config import settings
from database.database import get_db
from database.models.user import User, UserRole

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_id(token: Annotated[str, Depends(oauth2_bearer)]):
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



    except (JWTError, ValueError):
        raise credentials_exception

    return int(user_id)


user_id_dependency = Annotated[int, Depends(get_current_user_id)]


async def get_current_admin(user_id: user_id_dependency, db: AsyncSession = Depends(get_db)):
    user: User | None = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


db_dependency = Annotated[AsyncSession, Depends(get_db)]
admin_dependency = Annotated[User, Depends(get_current_admin)]
