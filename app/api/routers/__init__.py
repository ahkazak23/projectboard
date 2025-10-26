from fastapi import FastAPI

from . import auth, project


def register_routers(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(project.router)
