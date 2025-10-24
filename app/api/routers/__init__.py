from fastapi import FastAPI
from . import auth

def register_routers(app: FastAPI):
    app.include_router(auth.router)