import html
import telegram
from telegram.constants import ParseMode
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
sys_instruct = """
    You are a Personal Assistant named Neko. You speak in italian.
    
    You have specific tools available and MUST use them:

    1. For ANY web searches or current information: ALWAYS use perform_grounded_search tool
    2. For reminders: use create_reminder, get_reminders, update_reminder, delete_reminder tools
    3. For current time: use get_current_datetime tool

    NEVER invent or simulate responses. ALWAYS use the appropriate tool.

    Format responses using HTML tags:
    - <b>text</b> for bold
    - <i>text</i> for italic
    - <u>text</u> for underline
    - <s>text</s> for strikethrough
    - <pre>text</pre> for code
    - <a href="URL">text</a> for links
    - \n for line breaks (never use <br>)
    - <blockquote>text</blockquote> for quotes

    For lists:
    • Use bullet points with \n
    • Format important terms in <b>bold</b>
    • Use <i>italic</i> for emphasis

    IMPORTANT: 
    - ALWAYS use tools for real-time data
    - NEVER generate fictional responses
    - Use ONLY HTML formatting, no Markdown
    - Always include source links when using web search
"""

    # the expected output must be in html format, only the html and nothing else

# --- Funzioni di utilità ---
def get_user_id(update: telegram.Update) -> int:
    """Estrae l'ID utente da un oggetto Update di Telegram."""
    return update.effective_user.id

def escape_html(text: str) -> str:
    """Gestisce la formattazione del testo per Telegram"""
    # Rimuove le righe che contengono ```
    lines = text.splitlines()
    lines = [line for line in lines if '```' not in line]
    text = '\n'.join(lines)
    
    # Sostituisce i tag <br> con \n
    text = text.replace('<br>', '\n')
    text = text.replace('<br/>', '\n')
    text = text.replace('<br />', '\n')
    text = text.replace('<div>', '')
    text = text.replace('</div>', '')
    text = text.replace('<li>', '• ')
    text = text.replace('</li>', '\n')
    text = text.replace('<ul>', '\n')
    text = text.replace('</ul>', '\n')
    
    # Usa html.escape() per gestire tutti i caratteri speciali
    text = html.escape(text)
    
    # Ripristina i tag HTML validi
    valid_tags = [
        '<b>', '</b>', 
        '<i>', '</i>', 
        '<u>', '</u>', 
        '<s>', '</s>',
        '<a href', '\'>', '">', '</a>',
        '<pre>', '</pre>',
        '<code>', '</code>',
        '<blockquote>', '</blockquote>',
        '\'', '"'
    ]
    
    for tag in valid_tags:
        text = text.replace(html.escape(tag), tag)
    
    return text.strip()

async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    import re
    """Gestisce il comando /start."""
    welcome_message = (
        "<b>Benvenuto in MemoGenius!</b>\n\n"
        "Sono il tuo assistente personale. Posso aiutarti a:\n"
        "• Creare promemoria\n"
        "• Visualizzare i tuoi impegni\n"
        "• Modificare o eliminare promemoria\n"
        "• Cercare informazioni sul web\n\n"
        "<i>Dimmi cosa posso fare per te!</i>\n"
        "<a href='https://www.google.com'>google</a>"
    )
    
    print(escape_html(welcome_message))

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=escape_html(welcome_message),
        parse_mode=ParseMode.HTML
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
config = types.GenerateContentConfig(tools=tools, system_instruction=sys_instruct, temperature=0.0)
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
            # print(response.text)
            # formatted_text = response.text
            formatted_text = escape_html(response.text)
            # print(formatted_text)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=formatted_text,
                parse_mode=ParseMode.HTML
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
