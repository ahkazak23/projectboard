from fastapi import FastAPI

from . import auth, project, document


def register_routers(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(project.router)
    app.include_router(document.router)