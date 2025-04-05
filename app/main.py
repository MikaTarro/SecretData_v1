# from fastapi import FastAPI, HTTPException, Request
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime, timezone
# import redis
# from cryptography.fernet import Fernet
# import logging
#
# # Настройки базы данных
# DATABASE_URL = "postgresql://username:password@db/dbname"  # Замените на свои данные
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# # Настройки Redis
# redis_client = redis.Redis(host='redis', port=6379, db=0)
#
# # Генерация ключа для шифрования
# # Рекомендуется сохранять ключ в безопасном месте
# encryption_key = Fernet.generate_key()  # Замените на постоянный ключ, если нужно
# cipher = Fernet(encryption_key)
#
# # Настройка логирования
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Модель для секретов
# class Secret(Base):
#     __tablename__ = "secrets"
#     id = Column(Integer, primary_key=True, index=True)
#     key = Column(String, unique=True, index=True)
#     secret = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))
#
# # Модель для логов
# class ActionLog(Base):
#     __tablename__ = "action_logs"
#     id = Column(Integer, primary_key=True, index=True)
#     action = Column(String, index=True)
#     timestamp = Column(DateTime, default=datetime.now(timezone.utc))
#     ip_address = Column(String)
#
# # Создание таблиц
# Base.metadata.create_all(bind=engine)
#
# # Модель для запроса
# class SecretRequest(BaseModel):
#     key: str
#     secret: str
#
# app = FastAPI()
#
# @app.middleware("http")
# async def add_no_cache_header(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Cache-Control"] = "no-store"
#     response.headers["Pragma"] = "no-cache"
#     return response
#
# @app.post("/secrets/")
# def create_secret(secret_request: SecretRequest, request: Request):
#     db = SessionLocal()
#     try:
#         # Проверка, существует ли секрет
#         if redis_client.exists(secret_request.key):
#             raise HTTPException(status_code=400, detail="Secret already exists or has been accessed.")
#
#         # Шифрование секрета
#         encrypted_secret = cipher.encrypt(secret_request.secret.encode())
#
#         # Сохранение секрета в базе данных
#         new_secret = Secret(key=secret_request.key, secret=encrypted_secret.decode())
#         db.add(new_secret)
#         db.commit()
#         db.refresh(new_secret)
#
#         # Кеширование секрета в Redis на 5 минут
#         redis_client.set(secret_request.key, encrypted_secret.decode(), ex=300)
#
#         # Логирование действия
#         log_action("create_secret", request.client.host)
#
#         return {"message": "Secret created successfully."}
#     finally:
#         db.close()
#
# @app.get("/secrets/{key}")
# def get_secret(key: str, request: Request):
#     # Проверка кеша
#     secret = redis_client.get(key)
#     if secret:
#         # Удаление секрета из кеша
#         redis_client.delete(key)
#         decrypted_secret = cipher.decrypt(secret).decode("utf-8")
#         log_action("get_secret", request.client.host)
#         return {"secret": decrypted_secret}
#
#     # Проверка базы данных
#     db = SessionLocal()
#     try:
#         secret_record = db.query(Secret).filter(Secret.key == key).first()
#         if secret_record:
#             # Удаление секрета из базы данных
#             db.delete(secret_record)
#             db.commit()
#             decrypted_secret = cipher.decrypt(secret_record.secret.encode()).decode("utf-8")
#             log_action("get_secret", request.client.host)
#             return {"secret": decrypted_secret}
#         else:
#             raise HTTPException(status_code=404, detail="Secret not found.")
#     finally:
#         db.close()
#
# @app.delete("/secrets/{key}")
# def delete_secret(key: str, request: Request):
#     # Удаление секрета из кеша Redis
#     redis_client.delete(key)
#
#     # Удаление секрета из базы данных
#     db = SessionLocal()
#     try:
#         secret_record = db.query(Secret).filter(Secret.key == key).first()
#         if secret_record:
#             db.delete(secret_record)
#             db.commit()
#             log_action("delete_secret", request.client.host)
#             return {"message": "Secret deleted successfully."}
#         else:
#             raise HTTPException(status_code=404, detail="Secret not found.")
#     finally:
#         db.close()
#
# @app.post("/secrets/decode/{key}")
# def decode_secret(key: str, request: Request):
#     # Проверка кеша
#     secret = redis_client.get(key)
#     if secret:
#         decrypted_secret = cipher.decrypt(secret).decode("utf-8")
#         log_action("decode_secret", request.client.host)
#         return {"secret": decrypted_secret}
#
#     # Проверка базы данных
#     db = SessionLocal()
#     try:
#         secret_record = db.query(Secret).filter(Secret.key == key).first()
#         if secret_record:
#             decrypted_secret = cipher.decrypt(secret_record.secret.encode()).decode("utf-8")
#             log_action("decode_secret", request.client.host)
#             return {"secret": decrypted_secret}
#         else:
#             raise HTTPException(status_code=404, detail="Secret not found.")
#     finally:
#         db.close()
#
#
# def log_action(action: str, ip_address: str):
#     db = SessionLocal()
#     try:
#         log_entry = ActionLog(action=action, ip_address=ip_address)
#         db.add(log_entry)
#         db.commit()
#     except Exception as e:
#         db.rollback()
# #DONE!!
from fastapi import FastAPI
from app.routes import secrets

app = FastAPI()

app.include_router(secrets.router)
