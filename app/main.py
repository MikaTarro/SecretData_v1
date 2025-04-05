
from fastapi import FastAPI
from app.routes import secrets

app = FastAPI(title="SecretData_v1")

app.include_router(secrets.router)
