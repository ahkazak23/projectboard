from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.session import get_db
from app.services import auth as auth_svc
from app.core.errors import UserExistsError, AuthError
from app.schemas.auth import UserOut, TokenOut, RegisterIn, LoginIn


router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterIn, db: Session = Depends(get_db)):
    try:
        return auth_svc.register(db, login=data.login, password=data.password)
    except UserExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=TokenOut)
def login_user(data: LoginIn, db: Session = Depends(get_db)):
    try:
        token,expires_in = auth_svc.login(db, login=data.login, password=data.password)
        return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
