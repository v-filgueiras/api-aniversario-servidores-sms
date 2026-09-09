import math
from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import extract, func, or_
from sqlalchemy.orm import Session

from database.connect import SessionLocal
from models.employees_database import Employee, SendHistory
from services.birthday_service import send_daily_birthdays
from services.import_helpers import (
    is_valid_email,
    parse_active,
    parse_birth_date,
    read_spreadsheet,
)

router = APIRouter(prefix="/api")

MONTH_NAMES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------- schemas --

class EmployeeIn(BaseModel):
    full_name: str
    email: str
    birth_date: date
    active: bool = True

    @field_validator("full_name")
    @classmethod
    def name_not_blank(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Nome muito curto")
        return v

    @field_validator("email")
    @classmethod
    def email_is_valid(cls, v):
        v = v.strip().lower()
        if not is_valid_email(v):
            raise ValueError("E-mail inválido")
        return v


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    birth_date: date
    active: bool


# ----------------------------------------------------------------- health --

@router.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------------------- employees -

@router.get("/employees")
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: str = Query(""),
    active: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)

    q = q.strip()
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Employee.full_name.ilike(like), Employee.email.ilike(like)))

    if active in ("true", "false"):
        query = query.filter(Employee.active == (active == "true"))

    total = query.count()
    pages = max(1, math.ceil(total / page_size))
    page = min(page, pages)

    items = (
        query.order_by(Employee.full_name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [EmployeeOut.model_validate(e) for e in items],
        "page": page,
        "pages": pages,
        "total": total,
    }


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")
    return employee


@router.post("/employees", response_model=EmployeeOut)
def create_employee(payload: EmployeeIn, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Já existe um servidor com este e-mail")

    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeIn, db: Session = Depends(get_db)):
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")

    duplicate = db.query(Employee).filter(
        Employee.email == payload.email, Employee.id != employee_id
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Já existe um servidor com este e-mail")

    for field, value in payload.model_dump().items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.patch("/employees/{employee_id}/active", response_model=EmployeeOut)
def toggle_employee_active(employee_id: int, active: bool, db: Session = Depends(get_db)):
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")

    employee.active = active
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Servidor não encontrado")

    db.delete(employee)
    db.commit()
    return {"message": "Servidor excluído"}


# -------------------------------------------------------------- dashboard --

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    today = date.today()
    today_start = datetime.combine(today, time.min)

    employees_total = db.query(Employee).count()
    active_total = db.query(Employee).filter(Employee.active == True).count()

    birthdays_today = db.query(Employee).filter(
        extract("month", Employee.birth_date) == today.month,
        extract("day", Employee.birth_date) == today.day,
        Employee.active == True,
    ).count()

    birthdays_month = db.query(Employee).filter(
        extract("month", Employee.birth_date) == today.month,
        Employee.active == True,
    ).count()

    sent_today = db.query(SendHistory).filter(
        SendHistory.status == "sent", SendHistory.sent_at >= today_start
    ).count()

    failed_today = db.query(SendHistory).filter(
        SendHistory.status == "failed", SendHistory.sent_at >= today_start
    ).count()

    return {
        "employees_total": employees_total,
        "active_total": active_total,
        "birthdays_today": birthdays_today,
        "birthdays_month": birthdays_month,
        "sent_today": sent_today,
        "failed_today": failed_today,
    }


# -------------------------------------------------------------- birthdays --

@router.get("/birthdays/today")
def birthdays_today(db: Session = Depends(get_db)):
    today = date.today()

    employees = db.query(Employee).filter(
        extract("month", Employee.birth_date) == today.month,
        extract("day", Employee.birth_date) == today.day,
        Employee.active == True,
    ).order_by(Employee.full_name).all()

    return {"items": [EmployeeOut.model_validate(e) for e in employees]}


@router.get("/birthdays/month")
def birthdays_month(month: int = Query(..., ge=1, le=12), db: Session = Depends(get_db)):
    employees = db.query(Employee).filter(
        extract("month", Employee.birth_date) == month
    ).order_by(extract("day", Employee.birth_date)).all()

    return {"items": [EmployeeOut.model_validate(e) for e in employees], "month": month, "month_name": MONTH_NAMES_PT[month]}


@router.post("/birthdays/send")
def birthdays_send(db: Session = Depends(get_db)):
    return send_daily_birthdays(db)


# ------------------------------------------------------------------ import -

@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = read_spreadsheet(file.filename, file.file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    existing_emails = {e[0] for e in db.query(Employee.email).all()}
    seen_in_file = set()

    rows = []
    errors = []
    duplicate_in_file = 0

    for position, row in df.iterrows():
        line = position + 2

        try:
            full_name = str(row["full_name"]).strip()
            email = str(row["email"]).strip().lower()
            birth_date = parse_birth_date(row["birth_date"])
            active = parse_active(row["active"])

            if len(full_name) < 2 or full_name.lower() == "nan":
                raise ValueError("nome inválido")
            if not is_valid_email(email):
                raise ValueError("e-mail inválido")

            if email in seen_in_file:
                duplicate_in_file += 1
                continue
            seen_in_file.add(email)

            rows.append({
                "full_name": full_name,
                "email": email,
                "birth_date": birth_date.isoformat(),
                "active": active,
                "exists_in_database": email in existing_emails,
            })

        except Exception as error:
            errors.append({"line": line, "error": str(error)})

    total_rows = len(df)
    valid_rows = len(rows)

    summary = {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": len(errors),
        "already_in_database": sum(1 for r in rows if r["exists_in_database"]),
        "duplicate_in_file": duplicate_in_file,
    }

    return {"summary": summary, "errors": errors, "rows": rows}


@router.post("/import/commit")
async def import_commit(
    mode: str = Query("upsert", pattern="^(upsert|skip)$"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        df = read_spreadsheet(file.filename, file.file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    existing = {e.email: e for e in db.query(Employee).all()}
    seen_in_file = set()

    created, updated, skipped = 0, 0, 0

    for _, row in df.iterrows():
        try:
            full_name = str(row["full_name"]).strip()
            email = str(row["email"]).strip().lower()
            birth_date = parse_birth_date(row["birth_date"])
            active = parse_active(row["active"])

            if len(full_name) < 2 or not is_valid_email(email) or email in seen_in_file:
                skipped += 1
                continue

            seen_in_file.add(email)

        except Exception:
            skipped += 1
            continue

        if email in existing:
            if mode == "skip":
                skipped += 1
                continue

            employee = existing[email]
            employee.full_name = full_name
            employee.birth_date = birth_date
            employee.active = active
            updated += 1
        else:
            employee = Employee(
                full_name=full_name, email=email, birth_date=birth_date, active=active
            )
            db.add(employee)
            existing[email] = employee
            created += 1

    db.commit()

    return {"created": created, "updated": updated, "skipped": skipped}


# ----------------------------------------------------------------- history --

@router.get("/history")
def history(
    page_size: int = Query(50, ge=1, le=500),
    status: str = Query(""),
    target_date: str = Query(""),
    db: Session = Depends(get_db),
):
    query = db.query(SendHistory)

    if status:
        query = query.filter(SendHistory.status == status)

    if target_date:
        try:
            day = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Data inválida, use AAAA-MM-DD")

        day_start = datetime.combine(day, time.min)
        day_end = datetime.combine(day, time.max)
        query = query.filter(SendHistory.sent_at >= day_start, SendHistory.sent_at <= day_end)

    items = query.order_by(SendHistory.sent_at.desc()).limit(page_size).all()

    return {
        "items": [
            {
                "id": h.id,
                "full_name": h.full_name,
                "recipient_email": h.recipient_email,
                "status": h.status,
                "error_message": h.error_message,
                "provider_id": h.provider_id,
                "sent_at": h.sent_at.isoformat() if h.sent_at else None,
            }
            for h in items
        ]
    }
