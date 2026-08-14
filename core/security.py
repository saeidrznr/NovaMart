from datetime import timedelta, datetime, timezone

from pwdlib import PasswordHash
from jose import jwt

from core.config import settings
import secrets
import hashlib

passwordHash = PasswordHash.recommended()


def hash_password(password):
    return passwordHash.hash(password)


def verify_password(password, hashed_password):
    return passwordHash.verify(password, hashed_password)


def create_refresh_token():
    return secrets.token_urlsafe(64)


def hash_refresh_token(refresh_token):
    return hashlib.sha256(refresh_token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
