from sqlalchemy.orm import Session
from . import models, schemas
from .dependencies import get_from_user_id

def create_reminder(db: Session, reminder: schemas.ReminderCreate):
    db_reminder = models.Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminders(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    user = get_from_user_id(db, user_id)
    return db.query(models.Reminder)\
        .filter(models.Reminder.user_id == user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_reminder(db: Session, reminder_id: int, user_id: int):
    user = get_from_user_id(db, user_id)
    return db.query(models.Reminder)\
        .filter(models.Reminder.id == reminder_id)\
        .filter(models.Reminder.user_id == user.id)\
        .first()

def update_reminder(db: Session, reminder_id: int, reminder: schemas.ReminderUpdate, user_id: int):
    user = get_from_user_id(db, user_id)
    db_reminder = db.query(models.Reminder)\
        .filter(models.Reminder.id == reminder_id)\
        .filter(models.Reminder.user_id == user.id)\
        .first()
    if db_reminder:
        for key, value in reminder.model_dump().items():
            setattr(db_reminder, key, value)
        db.commit()
        db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: int, user_id: int):
    user = get_from_user_id(db, user_id)
    db_reminder = db.query(models.Reminder)\
        .filter(models.Reminder.id == reminder_id)\
        .filter(models.Reminder.user_id == user.id)\
        .first()
    if db_reminder:
        db.delete(db_reminder)
        db.commit()
    return db_reminder
