from datetime import date, datetime

from sqlalchemy import extract
from sqlalchemy.orm import Session

from models.employees_database import Employee, SendHistory

from services.card_service import (
    generate_birthday_card
)

from services.email_service import (
    send_email
)


def _already_sent_today(db: Session, employee_id: int) -> bool:
    today_start = datetime.combine(date.today(), datetime.min.time())

    return db.query(SendHistory).filter(
        SendHistory.employee_id == employee_id,
        SendHistory.status == "sent",
        SendHistory.sent_at >= today_start,
    ).first() is not None


def send_daily_birthdays(db: Session):

    today = date.today()

    employees = db.query(Employee).filter(
        extract("month", Employee.birth_date) == today.month,
        extract("day", Employee.birth_date) == today.day,
        Employee.active == True

    ).all()

    if not employees:
        return {
            "message": "No birthdays today",
            "sent": 0,
            "skipped": 0,
            "failed": 0,
        }

    sent, skipped, failed = 0, 0, 0

    for employee in employees:

        if _already_sent_today(db, employee.id):
            skipped += 1
            db.add(SendHistory(
                employee_id=employee.id,
                full_name=employee.full_name,
                recipient_email=employee.email,
                status="skipped",
                error_message="Já enviado hoje",
            ))
            db.commit()
            continue

        try:
            card_path = generate_birthday_card(employee.full_name)

            response = send_email(
                to_email=employee.email,
                employee_name=employee.full_name,
                card_path=card_path,
            )

            sent += 1
            db.add(SendHistory(
                employee_id=employee.id,
                full_name=employee.full_name,
                recipient_email=employee.email,
                status="sent",
                provider_id=(response or {}).get("id") if isinstance(response, dict) else None,
            ))

        except Exception as error:
            failed += 1
            db.add(SendHistory(
                employee_id=employee.id,
                full_name=employee.full_name,
                recipient_email=employee.email,
                status="failed",
                error_message=str(error),
            ))

        db.commit()

    return {
        "message": "Birthday emails processed",
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }
