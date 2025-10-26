from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status


class UserExistsError(Exception):
    pass

class AuthError(Exception):
    pass


def permission_error_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Forbidden"},
    )

def value_error_handler(request: Request, exc: ValueError):
    msg = str(exc)
    if msg == "NOT_FOUND":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Project not found"},
        )
    if msg == "TARGET_NOT_FOUND":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "User not found"},
        )
    if msg == "ALREADY_MEMBER":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Already a member"},
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": msg or "Bad Request"},
    )

def user_exists_error_handler(request: Request, exc: UserExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "User already exists"},
    )

def auth_error_handler(request: Request, exc: AuthError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


# Registrar
def register_exception_handlers(app) -> None:
    app.add_exception_handler(PermissionError, permission_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(UserExistsError, user_exists_error_handler)
    app.add_exception_handler(AuthError, auth_error_handler)