# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import reminders, database, schemas, models  # Import local modules
from .database import get_db

app = FastAPI()

# Initialize database tables (if they don't exist)
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# --- Routes for reminders ---
@app.post("/reminders/", response_model=schemas.Reminder)
def create_reminder(reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    return reminders.create_reminder(db=db, reminder=reminder)

@app.get("/reminders/", response_model=list[schemas.Reminder])
def read_reminders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return reminders.get_reminders(db, skip=skip, limit=limit)

@app.get("/reminders/{reminder_id}", response_model=schemas.Reminder)
def read_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = reminders.get_reminder(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@app.put("/reminders/{reminder_id}", response_model=schemas.Reminder)
def update_reminder(reminder_id: int, reminder: schemas.ReminderUpdate, db: Session = Depends(get_db)):
     db_reminder = reminders.update_reminder(db=db, reminder_id=reminder_id, reminder=reminder)
     if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
     return db_reminder

@app.delete("/reminders/{reminder_id}", response_model=schemas.Reminder)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = reminders.delete_reminder(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

