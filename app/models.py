from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Secret(Base):
    __tablename__ = "secrets"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    secret = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class ActionLog(Base):
    __tablename__ = "action_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    ip_address = Column(String)
