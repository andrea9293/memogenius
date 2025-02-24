from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import reminders, database, schemas, models
from .database import get_db
from .chat_handler import ChatHandler
from .schemas import ChatMessage
from .dependencies import get_current_user

app = FastAPI()
chat_handler = ChatHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=database.engine)

@app.post("/auth/web-login", response_model=schemas.User)
def web_login(
    access_key: str = Body(...),
    web_token: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.access_key == access_key).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid access key")
    
    user.web_token = web_token
    db.commit()
    db.refresh(user)
    return user

@app.post("/chat/message")
async def handle_chat_message(
    message: ChatMessage,
    current_user: models.User = Depends(get_current_user)
):
    response = await chat_handler.handle_message(
        message.message,
        current_user.telegram_id
        # current_user.id
    )
    return response

@app.post("/reminders/", response_model=schemas.Reminder)
def create_reminder(
    reminder: schemas.ReminderCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder.user_id = current_user.id
    return reminders.create_reminder(db=db, reminder=reminder)

@app.get("/reminders/", response_model=list[schemas.Reminder])
def read_reminders(
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    print(f"Reading reminders for user {current_user.id}")
    reminders_list = reminders.get_reminders(
        db=db, 
        user_id=current_user.id,
        skip=skip, 
        limit=limit
    )
    print(f"Found {len(reminders_list)} reminders")
    return reminders_list

@app.get("/reminders/{reminder_id}", response_model=schemas.Reminder)
def read_reminder(
    reminder_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_reminder = reminders.get_reminder(
        db=db, 
        reminder_id=reminder_id,
        user_id=current_user.id
    )
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@app.put("/reminders/{reminder_id}", response_model=schemas.Reminder)
def update_reminder(
    reminder_id: int,
    reminder: schemas.ReminderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_reminder = reminders.update_reminder(
        db=db, 
        reminder_id=reminder_id, 
        reminder=reminder,
        user_id=current_user.id
    )
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@app.delete("/reminders/{reminder_id}", response_model=schemas.Reminder)
def delete_reminder(
    reminder_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_reminder = reminders.delete_reminder(
        db=db, 
        reminder_id=reminder_id,
        user_id=current_user.id
    )
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder
