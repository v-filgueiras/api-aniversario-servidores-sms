from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from datetime import datetime

from database.connect import Base

class Employee(Base):
    
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, nullable=False)

    full_name = Column(String(150), nullable=False, unique=True)

    email = Column(String(250), nullable=False, unique=True)

    birth_date = Column(Date, nullable=False)

    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now)