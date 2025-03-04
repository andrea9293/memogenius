# app/gemini_tools.py
import requests
from datetime import datetime
from typing import List, Dict, Any
from google.genai import types
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from .config import settings
from .database import SessionLocal
from . import models, reminders, schemas

BASE_API_URL = "http://127.0.0.1:8000"  # FastAPI base URL

# --- Function Declarations (for Gemini) ---

create_reminder_declaration = types.FunctionDeclaration(
    name="create_reminder",
    description="Create a new reminder for the user.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "text": types.Schema(type=types.Type.STRING, description="The reminder text content."),
            "due_date": types.Schema(
                type=types.Type.STRING,
                description="Reminder date and time (ISO 8601 format, e.g. 2024-12-25T10:00:00).",
            ),
        },
        required=["text", "due_date"],
    ),
)

get_reminders_declaration = types.FunctionDeclaration(
    name="get_reminders",
    description="Retrieve user's reminders.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "skip": types.Schema(
                type=types.Type.INTEGER, description="Number of reminders to skip (for pagination)."
            ),
            "limit": types.Schema(
                type=types.Type.INTEGER, description="Maximum number of reminders to return."
            ),
        },
        required=[],  # No required parameters
    ),
)

update_reminder_declaration = types.FunctionDeclaration(
    name="update_reminder",
    description="Update an existing reminder.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "reminder_id": types.Schema(type=types.Type.INTEGER, description="ID of the reminder to update."),
            "text": types.Schema(type=types.Type.STRING, description="New reminder text content."),
            "due_date": types.Schema(
                type=types.Type.STRING,
                description="New reminder date and time (ISO 8601 format).",
            ),
            "is_active": types.Schema(
                type=types.Type.BOOLEAN, description="New reminder status, True if active, False otherwise."
            ),
        },
        required=["reminder_id","text", "due_date", "is_active"],
    ),
)

delete_reminder_declaration = types.FunctionDeclaration(
    name="delete_reminder",
    description="Delete a reminder.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"reminder_id": types.Schema(type=types.Type.INTEGER, description="ID of the reminder to delete.")},
        required=["reminder_id"],
    ),
)

perform_grounded_search_declaration = types.FunctionDeclaration(
    name="perform_grounded_search",
    description="Performs a web search to get real-time information. You MUST use this tool for ANY questions about current events, facts, weather, news, sports, or information you might not know. Never simulate web search results. The output should include dates and times in Italian format and timezone. Always include source links.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(type=types.Type.STRING, description="The specific search query that will give the most relevant results for the user's question."),
        },
        required=["query"],
    ),
)

get_current_datetime_declaration = types.FunctionDeclaration(
    name="get_current_datetime",
    description="Returns the current date and time. If you don't know exact time, use get_current_datetime tool without asking confirmation",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dummyParameter": types.Schema(
                type=types.Type.STRING,
                description="Unused dummy parameter",
            ),
        },
        required=[],  # No required parameters
    ),
)

# --- Functions that execute API calls ---

def get_user_id_from_identifier(db, identifier: int | str) -> int:
    """Converts telegram_id or web_token to the database user id"""
    user = None
    # First try as telegram_id
    if isinstance(identifier, int):
        user = db.query(models.User).filter(models.User.telegram_id == identifier).first()
    # Otherwise try as web_token
    if not user and isinstance(identifier, str):
        user = db.query(models.User).filter(models.User.web_token == identifier).first()
    if not user:
        user = db.query(models.User).filter(models.User.id == identifier).first()
    
    return user.id if user else None

def create_reminder_tool(user_id: int | str, text: str, due_date: str) -> Dict[str, Any]:
    print(f"Creating reminder for user identifier: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}

        try:
            due_date_dt = datetime.fromisoformat(due_date)
        except ValueError:
            return {"confirm_needed": "Ask confirmation for the due date and hour"}

        reminder_data = {
            "user_id": real_user_id,
            "text": text,
            "due_date": due_date_dt
        }
        result = reminders.create_reminder(db, schemas.ReminderCreate(**reminder_data))
        
        # Create a serializable dictionary instead of using __dict__
        return {
            "id": result.id,
            "text": result.text,
            "due_date": result.due_date.isoformat(),
            "is_active": result.is_active,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
            "user_id": result.user_id
        }
    finally:
        db.close()

def get_reminders_tool(user_id: int | str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    print(f"Fetching reminders for user identifier: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}

        reminders_list = reminders.get_reminders(db, real_user_id, skip, limit)
        # Proper serialization of reminder objects
        serialized_reminders = [
            {
                "id": reminder.id,
                "text": reminder.text,
                "due_date": reminder.due_date.isoformat(),
                "is_active": reminder.is_active,
                "created_at": reminder.created_at.isoformat(),
                "updated_at": reminder.updated_at.isoformat() if reminder.updated_at else None,
                "user_id": reminder.user_id
            }
            for reminder in reminders_list
        ]
        return serialized_reminders
    finally:
        db.close()

def update_reminder_tool(reminder_id: int, text: str | None = None, due_date: str | None = None, is_active: bool | None = None, user_id: int | None = None) -> Dict[str, Any]:
    print(f"Updating reminder: {reminder_id}")
    db = SessionLocal()
    try:
        update_data = {}
        if text is not None:
            update_data["text"] = text
        if due_date is not None:
            try:
                due_date_dt = datetime.fromisoformat(due_date)
                update_data["due_date"] = due_date_dt
            except ValueError:
                return {"error": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}
        if is_active is not None:
            update_data["is_active"] = is_active

        result = reminders.update_reminder(db, reminder_id, schemas.ReminderUpdate(**update_data), user_id)
        
        if result:
            return {
                "id": result.id,
                "text": result.text,
                "due_date": result.due_date.isoformat(),
                "is_active": result.is_active,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat() if result.updated_at else None,
                "user_id": result.user_id
            }
        else:
            return {"error": "Reminder not found"}
    finally:
        db.close()

def delete_reminder_tool(reminder_id: int, user_id: int | None = None) -> Dict[str, Any]:
    print(f"Deleting reminder: {reminder_id}")
    db = SessionLocal()
    try:
        result = reminders.delete_reminder(db, reminder_id, user_id)
        
        if result:
            return {
                "id": result.id,
                "text": result.text,
                "due_date": result.due_date.isoformat(),
                "is_active": result.is_active,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat() if result.updated_at else None,
                "user_id": result.user_id
            }
        else:
            return {"error": "Reminder not found"}
    finally:
        db.close()

def perform_deep_search(queryList: List[str], user_id: int | None = None) -> str:
    if len(queryList) > 10:
        return {"error": "You can perform a maximum of 10 queries at a time"}
    result = ''
    for query in queryList:
        result += "results for query: " + query + '\n' + perform_grounded_search(query, user_id) + '\n\n'
    return result
    
def perform_grounded_search(query: str, user_id: int | None = None) -> str:
    print(f"perform_grounded_search query: {query}")

    sys_instruct = """
        You are a web search expert who optimizes and transforms requests into effective web searches.
        Use exclusively your web search tool and only look for real, current results from the web.
        Don't just use bullet points, be more conversational
    """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model_id = "gemini-2.0-flash"

    google_search_tool = types.Tool(
        google_search = types.GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents=f"search on web using your GoogleSearch tool: {query}",
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
            temperature=0.0,
            system_instruction=sys_instruct
        )
    )
    
    res=''
    for each in response.candidates[0].content.parts:
        # print(each.text)
        res += each.text + '\n'

    # print(res)
    # print(response)
    
    res = res + ' | sources: ' + str(response.candidates[0].grounding_metadata.grounding_chunks)
    
    print(res)
    return res

def get_current_datetime(dummyParameter: str = "", user_id: int | None = None) -> str:
    """Returns current date and time in ISO 8601 format."""
    print("get_current_datetime")
    now = datetime.now()
    return now.isoformat()