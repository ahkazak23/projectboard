from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User

bearer = HTTPBearer(auto_error=False)
JWT_SECRET = settings.JWT_SECRET
JWT_ALG = settings.JWT_ALG

def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise _unauthorized()

    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except (ExpiredSignatureError, JWTError):
        raise _unauthorized()

    sub = payload.get("sub")
    if sub is None:
        raise _unauthorized()

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise _unauthorized()

    user = db.get(User, user_id)
    if not user:
        raise _unauthorized()

    return user