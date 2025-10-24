from typing import Tuple
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import UserExistsError, AuthError
from app.core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.models import User

def _normalize_login(login: str) -> str:
    return login.strip().lower()

def register(db: Session, *, login: str, password: str) -> User:
    norm_login = _normalize_login(login)

    exists = db.execute(select(User).where(User.login == norm_login)).scalar_one_or_none()
    if exists:
        raise UserExistsError("User already exists")

    user = User(login=norm_login, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise UserExistsError("User already exists")
    except SQLAlchemyError:
        db.rollback()
        raise

def login(db: Session, *, login: str, password: str) -> Tuple[str, int]:
    norm_login = _normalize_login(login)
    try:
        user = db.execute(select(User).where(User.login == norm_login)).scalar_one_or_none()
    except SQLAlchemyError:
        raise

    if not user or not verify_password(password,user.password_hash):
        raise AuthError("Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return token,ACCESS_TOKEN_EXPIRE_MINUTES*60