from fastapi import FastAPI
from . import auth, dep_test

def register_routers(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(dep_test.router)