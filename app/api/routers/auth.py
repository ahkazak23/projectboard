from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import auth as auth_svc
from app.schemas.auth import UserOut, TokenOut, RegisterIn, LoginIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterIn, db: Session = Depends(get_db)):
    return auth_svc.register(db, login=data.login, password=data.password)


@router.post("/login", response_model=TokenOut)
def login_user(data: LoginIn, db: Session = Depends(get_db)):
    token, expires_in = auth_svc.login(db, login=data.login, password=data.password)
    return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}
