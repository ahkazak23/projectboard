from fastapi import FastAPI
from app.api.routers import register_routers
from app.core.errors import register_exception_handlers
from app.db.session import engine, Base
import app.db.models

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"Status": "OK"}

register_routers(app)
register_exception_handlers(app)
