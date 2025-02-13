# app/gemini_tools.py
import requests
from datetime import datetime
from typing import List, Dict, Any
from google.genai import types
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from .config import settings

BASE_API_URL = "http://127.0.0.1:8000"  # URL di base dell'API FastAPI

# --- Dichiarazioni delle funzioni (per Gemini) ---

create_reminder_declaration = types.FunctionDeclaration(
    name="create_reminder",
    description="Crea un nuovo promemoria per l'utente.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "text": types.Schema(type=types.Type.STRING, description="Il testo del promemoria."),
            "due_date": types.Schema(
                type=types.Type.STRING,
                description="La data e l'ora del promemoria (formato ISO 8601, es. 2024-12-25T10:00:00).",
            ),
        },
        required=["text", "due_date"],
    ),
)

get_reminders_declaration = types.FunctionDeclaration(
    name="get_reminders",
    description="Ottiene i promemoria dell'utente.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "skip": types.Schema(
                type=types.Type.INTEGER, description="Il numero di promemoria da saltare (per la paginazione)."
            ),
            "limit": types.Schema(
                type=types.Type.INTEGER, description="Il numero massimo di promemoria da restituire."
            ),
        },
        required=[],  # Nessun parametro obbligatorio
    ),
)

update_reminder_declaration = types.FunctionDeclaration(
    name="update_reminder",
    description="Aggiorna un promemoria esistente.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "reminder_id": types.Schema(type=types.Type.INTEGER, description="L'ID del promemoria da aggiornare."),
            "text": types.Schema(type=types.Type.STRING, description="Il nuovo testo del promemoria."),
            "due_date": types.Schema(
                type=types.Type.STRING,
                description="La nuova data e ora del promemoria (formato ISO 8601).",
            ),
            "is_active": types.Schema(
                type=types.Type.BOOLEAN, description="Il nuovo stato del promemoria, True se è attivo, False altrimenti."
            ),
        },
        required=["reminder_id","text", "due_date", "is_active"],
    ),
)

delete_reminder_declaration = types.FunctionDeclaration(
    name="delete_reminder",
    description="Elimina un promemoria.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={"reminder_id": types.Schema(type=types.Type.INTEGER, description="L'ID del promemoria da eliminare.")},
        required=["reminder_id"],
    ),
)

perform_grounded_search_declaration = types.FunctionDeclaration(
    name="perform_grounded_search",
    description="Esegue una ricerca sul web per ottenere informazioni contestuali",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(type=types.Type.STRING, description="La query di ricerca."),
        },
        required=["query"],
    ),
)

get_current_datetime_declaration = types.FunctionDeclaration(
    name="get_current_datetime",
    description="Restituisce la data e l'ora correnti.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dummyParameter": types.Schema(
                type=types.Type.STRING,
                description="Parametro fittizio inutilizzato",
            ),
        },
        required=[],  # Nessun parametro obbligatorio
    ),
)

# --- Funzioni che eseguono le chiamate API ---

def create_reminder_tool(user_id: int, text: str, due_date: str) -> Dict[str, Any]:
    print("create_reminder_tool")
    """Crea un nuovo promemoria (chiamata API)."""
    try:
        due_date_dt = datetime.fromisoformat(due_date)
    except ValueError:
        return {"error": "Formato data non valido. Usa ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}

    payload = {"user_id": user_id, "text": text, "due_date": due_date_dt.isoformat()}
    response = requests.post(f"{BASE_API_URL}/reminders/", json=payload)
    response.raise_for_status()
    return response.json()


def get_reminders_tool(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    print("get_reminders_tool")
    """Ottiene i promemoria (chiamata API)."""
    params = {"user_id": user_id, "skip": skip, "limit": limit}
    response = requests.get(f"{BASE_API_URL}/reminders/", params=params)
    response.raise_for_status()
    return response.json()


def update_reminder_tool(reminder_id: int, text: str | None = None, due_date: str | None = None, is_active: bool | None = None) -> Dict[str, Any]:
    print("update_reminder_tool")
    """Aggiorna un promemoria (chiamata API)."""
    payload = {}
    if text is not None:
        payload["text"] = text
    if due_date is not None:
        try:
            due_date_dt = datetime.fromisoformat(due_date)
            payload["due_date"] = due_date_dt.isoformat()
        except ValueError:
            return {"error": "Formato data non valido. Usa ISO 8601 (YYYY-MM-DDTHH:MM:SS)."}
    if is_active is not None:
        payload["is_active"] = is_active

    if not payload:
        return {"error": "Nessun dato fornito per l'aggiornamento."}

    response = requests.put(f"{BASE_API_URL}/reminders/{reminder_id}", json=payload)
    response.raise_for_status()
    return response.json()


def delete_reminder_tool(reminder_id: int) -> Dict[str, Any]:
    print("delete_reminder_tool")
    """Elimina un promemoria (chiamata API)."""
    response = requests.delete(f"{BASE_API_URL}/reminders/{reminder_id}")
    response.raise_for_status()
    return response.json()

def perform_grounded_search(query: str) -> str:
    print("perform_grounded_search")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model_id = "gemini-2.0-flash"

    google_search_tool = types.Tool(
        google_search = types.GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents=query,
        config=types.GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )

    res=''
    for each in response.candidates[0].content.parts:
        # print(each.text)
        res += each.text + '\n'

    # print(res)
    # print(response)
    
    res = res + ' | sources: ' + str(response.candidates[0].grounding_metadata.grounding_chunks)
    
    # print(res)
    return res

def get_current_datetime(dummyParameter: str = "") -> str:
    """Restituisce la data e l'ora correnti in formato ISO 8601."""
    print("get_current_datetime")
    now = datetime.now()
    return now.isoformat()