from datetime import date

from sqlalchemy import extract
from sqlalchemy.orm import Session

from models.employees_database import Employee

from services.card_service import (
    generate_birthday_card
)

from services.email_service import (
    send_email
)


def send_daily_birthdays(
    db: Session
):

    today = date.today()

    employees = db.query(Employee).filter(
        extract(
            "month",
            Employee.birth_date
        ) == today.month,

        extract(
            "day",
            Employee.birth_date
        ) == today.day,

        Employee.active == True

    ).all()

    if not employees:

        return {
            "message": (
                "No birthdays today"
            )
        }

    sent_emails = []

    for employee in employees:

        # gera cartão
        card_path = generate_birthday_card(
            employee.full_name
        )

        # envia email
        send_email(
            to_email=employee.email,
            employee_name=employee.full_name,
            card_path=card_path
        )

        sent_emails.append(
            employee.email
        )

    return {
        "message": (
            "Birthday emails sent successfully"
        ),
        "total_sent": len(sent_emails),
        "emails": sent_emails
    }