from fastapi import FastAPI
from .session import engine
from .models import Base
from app.api.routers import auth as auth_router
app = FastAPI()
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"Status": "OK"}
app.include_router(auth_router.router)