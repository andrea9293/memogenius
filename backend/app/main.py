from fastapi import FastAPI, Depends, HTTPException, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import reminders, database, schemas, models
from .database import get_db, SessionLocal
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
    # Inizializza SQLite
    models.Base.metadata.create_all(bind=database.engine)
    
    # Inizializza esplicitamente ChromaDB
    from .memory_db import get_memory_db
    get_memory_db()
    
    # Crea le liste predefinite per tutti gli utenti esistenti
    from . import lists
    with SessionLocal() as db:  # Ora SessionLocal è definito
        users = db.query(models.User).all()
        for user in users:
            lists.ensure_user_lists_exist(db, user.id)

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
    # print(f"Reading reminders for user {current_user.id}")
    reminders_list = reminders.get_reminders(
        db=db, 
        user_id=current_user.id,
        skip=skip, 
        limit=limit
    )
    # print(f"Found {len(reminders_list)} reminders")
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

@app.post("/alexa/intent")
async def handle_alexa_intent(request: Request):
    data = await request.json()
    
    # Extract information from Alexa request
    session = data.get('session', {})
    intent_request = data.get('request', {})
    intent_type = intent_request.get('type')
    
    # Detailed logging for debugging
    print(f"Alexa request received: {intent_type}")
    print(f"Request details: {intent_request}")
    
    # Get or generate a stable user ID for Alexa
    alexa_user_id = "123456" #TODO Use a fixed user ID or session.get('user', {}).get('userId')
    
    # Handle different request types
    if intent_type == 'LaunchRequest':
        # Welcome message
        response_text = "Benvenuto in MemoGenius. Come posso aiutarti?"
    elif intent_type == 'IntentRequest':
        intent = intent_request.get('intent', {})
        intent_name = intent.get('name')
        
        # Only handle exit intents separately
        if intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
            response_text = "Arrivederci!"
            return {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "SSML",
                        "ssml": f"<speak>{response_text}</speak>"
                    },
                    "shouldEndSession": True  # Close the session to exit
                }
            }
        else:
            # For ALL other intents (including Help, Fallback, Query, etc.)
            # Extract user message in different possible ways
            user_message = ""
            
            # Try to get the message from the Message slot if available
            if 'slots' in intent and 'Message' in intent.get('slots', {}):
                user_message = intent.get('slots', {}).get('Message', {}).get('value', '')
                print(f"Message extracted from slot: '{user_message}'")
            
            # If there's no explicit message and it's HelpIntent
            if not user_message and intent_name == 'AMAZON.HelpIntent':
                user_message = "aiuto"
            
            # For FallbackIntent, use the recognized text if available
            if not user_message or intent_name == 'AMAZON.FallbackIntent':
                # When Alexa doesn't understand, suggest the correct pattern
                response_text = "Non ho capito. Prova a iniziare la tua frase con 'memo genius' seguito dalla tua richiesta."
                return {
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {
                            "type": "SSML",
                            "ssml": f"<speak>{response_text}</speak>"
                        },
                        "shouldEndSession": False,
                        "reprompt": {
                            "outputSpeech": {
                                "type": "SSML",
                                "ssml": "<speak>Puoi dire 'memo genius' seguito dalla tua domanda.</speak>"
                            }
                        }
                    }
                }
            
            # Send any message to the chat_handler
            print(f"Sending to chat_handler: '{user_message}'")
            response = await chat_handler.handle_message(user_message, alexa_user_id)
            response_text = response.get('text', 'Mi dispiace, non sono riuscito a elaborare la richiesta.')
    else:
        # For any other type of request (SessionEndedRequest, etc.)
        response_text = "Non ho capito. Puoi ripetere?"
    
    # Clean up text for Alexa (remove HTML)
    from html import unescape
    import re
    
    clean_text = re.sub(r'<[^>]*>', '', response_text)
    clean_text = unescape(clean_text)
    
    # Prepare the response while keeping the session open
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": f"<speak>{clean_text}</speak>"
            },
            "shouldEndSession": False,  # Keep the session open
            "reprompt": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": "<speak>Posso aiutarti con altro?</speak>"
                }
            }
        }
    }


