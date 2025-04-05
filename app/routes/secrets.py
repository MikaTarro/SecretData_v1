from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import Secret, ActionLog
from app.schemas import SecretRequest
from app.database import SessionLocal
from app.redis_client import redis_client
from app.encryption import cipher
from app.logging import logger
from datetime import datetime

router = APIRouter()

def log_action(action: str, ip_address: str):
    db = SessionLocal()
    try:
        log_entry = ActionLog(action=action, ip_address=ip_address)
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging action: {e}")
    finally:
        db.close()

@router.post("/")
def create_secret(secret_request: SecretRequest, request: Request):
    db = SessionLocal()
    try:
        # Проверка, существует ли секрет
        if redis_client.exists(secret_request.key):
            raise HTTPException(status_code=400, detail="Secret already exists or has been accessed.")

        # Шифрование секрета
        encrypted_secret = cipher.encrypt(secret_request.secret.encode())

        # Сохранение секрета в базе данных
        new_secret = Secret(key=secret_request.key, secret=encrypted_secret.decode())
        db.add(new_secret)
        db.commit()
        db.refresh(new_secret)

        # Кеширование секрета в Redis на 5 минут
        redis_client.set(secret_request.key, encrypted_secret.decode(), ex=300)

        # Логирование действия
        log_action("create_secret", request.client.host)

        return {"message": "Secret created successfully."}
    finally:
        db.close()

@router.get("/{key}")
def get_secret(key: str, request: Request):
    # Проверка кеша
    secret = redis_client.get(key)
    if secret:
        # Удаление секрета из кеша
        redis_client.delete(key)
        decrypted_secret = cipher.decrypt(secret).decode("utf-8")
        log_action("get_secret", request.client.host)
        return {"secret": decrypted_secret}

    # Проверка базы данных
    db = SessionLocal()
    try:
        secret_record = db.query(Secret).filter(Secret.key == key).first()
        if secret_record:
            # Удаление секрета из базы данных
            db.delete(secret_record)
            db.commit()
            decrypted_secret = cipher.decrypt(secret_record.secret.encode()).decode("utf-8")
            log_action("get_secret", request.client.host)
            return {"secret": decrypted_secret}
        else:
            raise HTTPException(status_code=404, detail="Secret not found.")
    finally:
        db.close()

@router.delete("/{key}")
def delete_secret(key: str, request: Request):
    # Удаление секрета из кеша Redis
    redis_client.delete(key)

    # Удаление секрета из базы данных
    db = SessionLocal()
    try:
        secret_record = db.query(Secret).filter(Secret.key == key).first()
        if secret_record:
            db.delete(secret_record)
            db.commit()
            log_action("delete_secret", request.client.host)
            return {"message": "Secret deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail="Secret not found.")
    finally:
        db.close()

@router.post("/decode/{key}")
def decode_secret(key: str, request: Request):
    # Проверка кеша
    secret = redis_client.get(key)
    if secret:
        decrypted_secret = cipher.decrypt(secret).decode("utf-8")
        log_action("decode_secret", request.client.host)
        return {"secret": decrypted_secret}

    # Проверка базы данных
    db = SessionLocal()
    try:
        secret_record = db.query(Secret).filter(Secret.key == key).first()
        if secret_record:
            decrypted_secret = cipher.decrypt(secret_record.secret.encode()).decode("utf-8")
            log_action("decode_secret", request.client.host)
            return {"secret": decrypted_secret}
        else:
            raise HTTPException(status_code=404, detail="Secret not found.")
    finally:
        db.close()
