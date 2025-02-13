# app/reminders.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_reminder(db: Session, reminder: schemas.ReminderCreate):
    db_reminder = models.Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Reminder).offset(skip).limit(limit).all()

def get_reminder(db: Session, reminder_id: int):
    return db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()

def update_reminder(db: Session, reminder_id: int, reminder: schemas.ReminderUpdate):
    db_reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if db_reminder:
        for key, value in reminder.model_dump().items():
            setattr(db_reminder, key, value)
        db.commit()
        db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: int):
    db_reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if db_reminder:
        db.delete(db_reminder)
        db.commit()
    return db_reminder
