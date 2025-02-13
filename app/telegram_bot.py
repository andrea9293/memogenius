import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown
from google import genai
from google.genai import types
from .config import settings
from . import gemini_tools
from .utils import format_reminder_for_display
from typing import Dict, Any

# Configura l'API di Gemini tramite il client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
sys_instruct= """
    
    You are a Personal Assistant. Your name is Neko. You can do some tasks like creating reminders, 
    getting reminders, updating reminders, and deleting reminders. You can also perform a grounded search. 
    when you have some links, always report in message with label that when cliecked forward to full link.    
    
    """
    # the expected output must be in html format, only the html and nothing else

# --- Funzioni di utilità ---
def get_user_id(update: telegram.Update) -> int:
    """Estrae l'ID utente da un oggetto Update di Telegram."""
    return update.effective_user.id

# --- Funzioni di gestione dei comandi Telegram ---

def escape_special_chars(text: str) -> str:
    # Lista completa dei caratteri che necessitano escape in MarkdownV2
    special_chars = ['~', '>', '#', '+', 
                    '-', '=', '|', '{', '}', ')', '.', '!']
    
    text = text.replace('\\n', '\n')
    
    # Escape di ogni carattere speciale
    for char in special_chars:
        text = text.replace(char, f'\{char}')
    return text

async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    import re
    """Gestisce il comando /start."""
    welcome_message = (
        "\#\# Benvenuto in MemoGenius\!\n\n"
        "*Benvenuto in MemoGenius\!*\n\n"
        "Sono il tuo assistente personale\. Posso aiutarti a:\n"
        "• Creare promemoria\n"
        "• Visualizzare i tuoi impegni\n"
        "• Modificare o eliminare promemoria\n"
        "\- Cercare informazioni sul web\n\n"
        "_Dimmi cosa posso fare per te\!_"
        "[google](https://www.google.com)"
        "``` [google](https://www.google.com) ```"
        "\{ [google](https://www.google.com) \}"
        "< [google](https://www.google.com) \>"
        # "*Benvenuto in MemoGenius\!*\n\n"
        # "Sono il tuo assistente personale\\. Posso aiutarti a:\n"
        # "• Creare promemoria\n"
        # "• Visualizzare i tuoi impegni\n"
        # "• Modificare o eliminare promemoria\n"
        # "• Cercare informazioni sul web\n\n"
        # "_Dimmi cosa posso fare per te\!_"
        # "[google](https://www.google.com)"
    )
    
    print(welcome_message)
    escaped_message = welcome_message
    # escaped_message = escape_special_chars(welcome_message)
    print(escaped_message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=escaped_message,
        parse_mode='MarkdownV2'
    )

# --- Funzione principale per l'interazione con Gemini ---

# Inizializza la chat FUORI da handle_message
tools = [
    types.Tool(function_declarations=[  # Tool per funzioni personalizzate
        gemini_tools.create_reminder_declaration,
        gemini_tools.get_reminders_declaration,
        gemini_tools.update_reminder_declaration,
        gemini_tools.delete_reminder_declaration,
        gemini_tools.perform_grounded_search_declaration,
        gemini_tools.get_current_datetime_declaration
    ])
]
config = types.GenerateContentConfig(tools=tools, system_instruction=sys_instruct)
chat = client.chats.create(model='gemini-2.0-flash', config=config)  # Inizializza la chat

async def handle_message(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi dell'utente, interagisce con Gemini e usa i tools."""
    user_id = get_user_id(update)
    user_message = update.message.text

    # Invia il messaggio dell'utente a Gemini
    response = chat.send_message(user_message)

    # Ciclo principale per gestire *tutte* le risposte di Gemini
    while True:  # Continua finché non c'è più niente da fare
        handled = False  # Flag per vedere se abbiamo gestito qualcosa

        if response.function_calls:
            for function_call in response.function_calls:
                function_name = function_call.name
                function_args = dict(function_call.args)

                if function_name == "create_reminder":
                    function_args['user_id'] = user_id
                    result = gemini_tools.create_reminder_tool(**function_args)
                elif function_name == "get_reminders":
                    function_args['user_id'] = user_id
                    result = gemini_tools.get_reminders_tool(**function_args)
                elif function_name == "update_reminder":
                    result = gemini_tools.update_reminder_tool(**function_args)
                elif function_name == "delete_reminder":
                    result = gemini_tools.delete_reminder_tool(**function_args)
                elif function_name == "perform_grounded_search":
                    result = gemini_tools.perform_grounded_search(**function_args)
                elif function_name == "get_current_datetime":
                    result = gemini_tools.get_current_datetime(**function_args)
                else:
                    result = {"error": f"Funzione sconosciuta: {function_name}"}

                # Invia la risposta della funzione a Gemini
                response = chat.send_message(
                    types.Content(
                        parts=[types.Part(function_response=types.FunctionResponse(name=function_name, response={"content": result}))],
                        role="function",
                    ),
                    config=config,
                )
                handled = True  # Abbiamo gestito una chiamata di funzione

        elif response.text:
            print(response.text)
            # formatted_text = response.text
            # formatted_text = escape_markdown(response.text, version=2)
            formatted_text = escape_special_chars(response.text)
            print(formatted_text)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=formatted_text,
                parse_mode='MarkdownV2'
            )
            handled = True  # Abbiamo gestito del testo
            break  # Esci dal ciclo dopo aver inviato il testo

        if not handled:
            # Se non abbiamo gestito né chiamate di funzione né testo,
            # probabilmente abbiamo finito.  Questo evita un loop infinito.
            break



def setup_telegram_bot():
    """Configura e avvia il bot Telegram."""
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Gestori dei comandi
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    # Gestore dei messaggi
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    app.add_handler(message_handler)

    return app

# --- Avvio del bot (da eseguire solo se questo file è eseguito direttamente) ---
if __name__ == '__main__':
    app = setup_telegram_bot()
    app.run_polling()
