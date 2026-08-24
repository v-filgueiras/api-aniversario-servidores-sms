from datetime import datetime
from database.connect import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String


class Employee(Base):
    __tablename__ = "api_aniversario_servidores"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    full_name = Column(String(150), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now)