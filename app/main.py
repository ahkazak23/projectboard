from fastapi import FastAPI
from .session import engine
from .models import Base

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"Status": "OK"}