from typing import Annotated

from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.user import User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)
JWT_SECRET = settings.JWT_SECRET
JWT_ALG = settings.JWT_ALG


def get_current_user(creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
                     db: Annotated[Session, Depends(get_db)]) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no subject")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: Expired token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, int(sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
