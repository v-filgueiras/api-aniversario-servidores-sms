from apscheduler.schedulers.background import BackgroundScheduler
from database.connect import SessionLocal
from services.birthday_service import send_daily_birthdays

scheduler = BackgroundScheduler()


def run_daily_birthdays():
    db = SessionLocal()
    try:
        result = send_daily_birthdays(db)
        print(f"Resultado do agendador: {result}")
    except Exception as error:
        print(f"Scheduler error: {error}")
    finally:
        db.close()

    
def start_scheduler():
    # Garante o envio às 07:00 da manhã no horário local de Três Lagoas - MS
    scheduler.add_job(
        run_daily_birthdays,
        trigger="cron",
        hour=7,
        minute=0,
        timezone="America/Campo_Grande",
    )

    scheduler.start()
    print("Birthday scheduler started (Horario de Tres Lagoas - MS)")