from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import date
from sqlalchemy.orm import Session
import pandas as pd

from database.connect import SessionLocal
from models.employees_database import Employee
from services.birthday_service import send_daily_birthdays

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PublicEmployee(BaseModel):
    full_name: str
    email: str
    birth_date: date
    active: bool


@router.post("/employees")
def create_employee(employee: PublicEmployee, db: Session = Depends(get_db)):
    
    new_employee = Employee(
        full_name = employee.full_name,
        email = employee.email,
        birth_date = employee.birth_date,
        active = employee.active
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee

@router.post("/employees/import")
async def import_employees(file: UploadFile = File(...),db: Session = Depends(get_db)):

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format"
        )

    for _, row in df.iterrows():

        employee = Employee(
            full_name=row["full_name"],
            email=row["email"],
            birth_date=row["birth_date"],
            active=row["active"]
        )

        db.add(employee)

    db.commit()

    return {
        "message": "Employees imported successfully"
    }

@router.post("/employees/send-birthday")
def send_birthdays(
    db: Session = Depends(get_db)
):

    return send_daily_birthdays(db)

@router.get("/employees/{name}")
def get_employee_by_id(name: str, db: Session = Depends(get_db)):
    
    employee = db.query(Employee).filter(
        Employee.full_name == name).first()
    
    return employee


@router.put("/employees/{name}")
def update_employee(
    name: str,
    employee_data: PublicEmployee,
    db: Session = Depends(get_db)
):

    employee = db.query(Employee).filter(
        Employee.full_name == name
    ).first()

    if not employee:
        return {"message": "Employee not found"}

    employee.full_name = employee_data.full_name
    employee.email = employee_data.email
    employee.birth_date = employee_data.birth_date
    employee.active = employee_data.active

    db.commit()
    db.refresh(employee)

    return employee

@router.delete("/employees/{name}")
def delete_employee_by_id(name: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.full_name == name).first()

    if not employee:
        raise HTTPException(status_code=404, detail="employee not found")
    
    db.delete(employee)
    db.commit()

    return f"User {employee.full_name}, deleted."
