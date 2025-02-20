# app/gemini_tools.py
import requests
from datetime import datetime
from typing import List, Dict, Any
from google.genai import types
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from .config import settings

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
    description="Performs a web search. The output should include dates and times in Italian format and timezone. Always include source links.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(type=types.Type.STRING, description="The search query."),
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

# --- Funzioni che eseguono le chiamate API ---

def create_reminder_tool(user_id: int, text: str, due_date: str) -> Dict[str, Any]:
    print("create_reminder_tool")
    """Creates a new reminder (API call)."""
    try:
        due_date_dt = datetime.fromisoformat(due_date)
    except ValueError:
        return {"error": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}

    payload = {"user_id": user_id, "text": text, "due_date": due_date_dt.isoformat()}
    response = requests.post(f"{BASE_API_URL}/reminders/", json=payload)
    response.raise_for_status()
    return response.json()


def get_reminders_tool(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    print("get_reminders_tool")
    """Retrieves reminders (API call)."""
    params = {"user_id": user_id, "skip": skip, "limit": limit}
    response = requests.get(f"{BASE_API_URL}/reminders/", params=params)
    response.raise_for_status()
    return response.json()


def update_reminder_tool(reminder_id: int, text: str | None = None, due_date: str | None = None, is_active: bool | None = None) -> Dict[str, Any]:
    print("update_reminder_tool")
    """Updates a reminder (API call)."""
    payload = {}
    if text is not None:
        payload["text"] = text
    if due_date is not None:
        try:
            due_date_dt = datetime.fromisoformat(due_date)
            payload["due_date"] = due_date_dt.isoformat()
        except ValueError:
            return {"error": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}
    if is_active is not None:
        payload["is_active"] = is_active

    if not payload:
        return {"error": "No data provided for update."}

    response = requests.put(f"{BASE_API_URL}/reminders/{reminder_id}", json=payload)
    response.raise_for_status()
    return response.json()


def delete_reminder_tool(reminder_id: int) -> Dict[str, Any]:
    print("delete_reminder_tool")
    """Deletes a reminder (API call)."""
    response = requests.delete(f"{BASE_API_URL}/reminders/{reminder_id}")
    response.raise_for_status()
    return response.json()

def perform_grounded_search(query: str) -> str:
    print("perform_grounded_search")

    sys_instruct = """
        You are a web search expert who optimizes and transforms requests into effective web searches.
        Use exclusively your web search tool and only look for real, current results from the web.
        Format all dates and times in Italian format and timezone.
        Always include and cite your sources.
    """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model_id = "gemini-2.0-flash"

    google_search_tool = types.Tool(
        google_search = types.GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents=f"search on web usign your GoogleSearch tool: {query}",
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
            temperature=0.0,
            system_instruction=sys_instruct
        )
    )
    
    print(response)

    res=''
    for each in response.candidates[0].content.parts:
        # print(each.text)
        res += each.text + '\n'

    # print(res)
    # print(response)
    
    res = res + ' | sources: ' + str(response.candidates[0].grounding_metadata.grounding_chunks)
    
    print(res)
    return res

def get_current_datetime(dummyParameter: str = "") -> str:
    """Returns current date and time in ISO 8601 format."""
    print("get_current_datetime")
    now = datetime.now()
    return now.isoformat()