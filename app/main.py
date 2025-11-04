from fastapi import FastAPI

import app.db.models
from app.api.routers import register_routers
from app.core.errors import register_exception_handlers

app = FastAPI(title="ProjectBoard API")


@app.get("/health")
def health():
    return {"Status": "OK"}


register_routers(app)
register_exception_handlers(app)
