# app/utils.py
from datetime import datetime
from typing import Dict, Any

def format_reminder_for_display(reminder: Dict[str, Any]) -> str:
    """Formatta un promemoria per la visualizzazione all'utente."""
    due_date_str = reminder['due_date']
    # Converti la stringa ISO 8601 in un oggetto datetime, se necessario
    if isinstance(due_date_str, str):
        due_date = datetime.fromisoformat(due_date_str)
    else:
        due_date = due_date_str
    formatted_date = due_date.strftime("%d/%m/%Y %H:%M")  # Formato italiano
    return f"ID: {reminder['id']}\nTesto: {reminder['text']}\nScadenza: {formatted_date}\nAttivo: {reminder['is_active']}"

