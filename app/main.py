
from fastapi import FastAPI
from app.routes import secrets

app = FastAPI()

app.include_router(secrets.router)
