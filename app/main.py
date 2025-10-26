from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.db.models
from app.api.routers import register_routers
from app.core.errors import register_exception_handlers
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"Status": "OK"}


register_routers(app)
register_exception_handlers(app)
