from datetime import datetime, timedelta, timezone
from os import getenv
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = getenv("JWT_SECRET", "changeme")
JWT_ALG = getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_ctx.verify(password, password_hash)


def create_access_token(
    subject: str, ttl_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ttl_minutes)
    payload: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
