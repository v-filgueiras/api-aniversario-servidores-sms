from datetime import datetime
from database.connect import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text


class Employee(Base):
    __tablename__ = "api_aniversario_servidores"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now)


class SendHistory(Base):
    __tablename__ = "birthday_send_history"

    id = Column(Integer, primary_key=True, nullable=False)
    employee_id = Column(Integer, ForeignKey("api_aniversario_servidores.id"), nullable=True)
    full_name = Column(String(150), nullable=False)
    recipient_email = Column(String(150), nullable=False)
    status = Column(String(20), nullable=False)
    error_message = Column(Text, nullable=True)
    provider_id = Column(String(120), nullable=True)
    sent_at = Column(DateTime, default=datetime.now)
