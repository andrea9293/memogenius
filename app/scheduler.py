import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from telegram.constants import ParseMode
from .database import SessionLocal
from . import models
from .telegram_bot import setup_telegram_bot

async def check_and_send_reminders_async():
    now = datetime.now()
    print("check_and_send_reminders at time ", now)
    db: Session = SessionLocal()
    try:
        due_reminders = db.query(models.Reminder).filter(
            models.Reminder.due_date <= now,
            models.Reminder.is_active == True
        ).all()

        if due_reminders:
            telegram_app = setup_telegram_bot()
            bot = telegram_app.bot  # ExtBot (asincrono)

            for reminder in due_reminders:
                message_text = f"⏰ <b>È ora di:</b>\n\n {reminder.text}"
                try:
                    # Uso di await
                    await bot.send_message(chat_id=reminder.user_id, text=message_text, parse_mode=ParseMode.HTML)
                    reminder.is_active = False
                except Exception as e:
                    print(f"Errore nell'invio del messaggio: {e}")

            db.commit()
    finally:
        db.close()

def check_and_send_reminders():
    # Esegui la funzione asincrona nel loop (bloccante)
    asyncio.run(check_and_send_reminders_async())

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_send_reminders, "interval", seconds=5)
scheduler.start()
