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

# Configure the Gemini API through the client
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
    - If you don't know exact time, use get_current_datetime tool without asking confirmation
"""

# --- Utility Functions ---
def get_user_id(update: telegram.Update) -> int:
    """Extracts the user ID from a Telegram Update object."""
    return update.effective_user.id

def escape_html(text: str) -> str:
    """Handles text formatting for Telegram"""
    # Remove lines containing ```
    lines = text.splitlines()
    lines = [line for line in lines if '```' not in line]
    text = '\n'.join(lines)
    
    # Replace <br> tags with \n
    text = text.replace('<br>', '\n')
    text = text.replace('<br/>', '\n')
    text = text.replace('<br />', '\n')
    text = text.replace('<div>', '')
    text = text.replace('</div>', '')
    text = text.replace('<li>', '• ')
    text = text.replace('</li>', '\n')
    text = text.replace('<ul>', '\n')
    text = text.replace('</ul>', '\n')
    
    # Use html.escape() to handle all special characters
    text = html.escape(text)
    
    # Restore valid HTML tags
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
    """Handles the /start command."""
    welcome_message = (
        "<b>Welcome to MemoGenius!</b>\n\n"
        "I'm your personal assistant. I can help you:\n"
        "• Create reminders\n"
        "• View your appointments\n"
        "• Modify or delete reminders\n"
        "• Search information on the web\n\n"
        "<i>Tell me what I can do for you!</i>\n"
    )
    
    print(escape_html(welcome_message))

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=escape_html(welcome_message),
        parse_mode=ParseMode.HTML
    )

# --- Main function for Gemini interaction ---

# Initialize chat OUTSIDE handle_message
tools = [
    types.Tool(function_declarations=[  # Tool for custom functions
        gemini_tools.create_reminder_declaration,
        gemini_tools.get_reminders_declaration,
        gemini_tools.update_reminder_declaration,
        gemini_tools.delete_reminder_declaration,
        gemini_tools.perform_grounded_search_declaration,
        gemini_tools.get_current_datetime_declaration
    ])
]
config = types.GenerateContentConfig(tools=tools, system_instruction=sys_instruct, temperature=0.0)
chat = client.chats.create(model='gemini-2.0-flash', config=config)  # Initialize chat

async def handle_message(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user messages, interacts with Gemini and uses tools."""
    user_id = get_user_id(update)
    user_message = update.message.text

    print(f"User {user_id} sent message: {user_message}")
    # Send user message to Gemini
    response = chat.send_message(user_message)

    # Main loop to handle ALL Gemini responses
    while True:  # Continue until there's nothing left to do
        handled = False  # Flag to see if we handled something

        if response.function_calls:
            # print(f"Function calls: {response.function_calls}")
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
                    result = {"error": f"Unknown function: {function_name}"}

                # Send function response to Gemini
                response = chat.send_message(
                    types.Content(
                        parts=[types.Part(function_response=types.FunctionResponse(name=function_name, response={"content": result}))],
                        role="function",
                    ),
                    config=config,
                )
                handled = True  # We handled a function call

        elif response.text:
            formatted_text = escape_html(response.text)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=formatted_text,
                parse_mode=ParseMode.HTML
            )
            handled = True  # We handled text
            break  # Exit loop after sending text

        if not handled:
            # If we haven't handled either function calls or text,
            # we're probably done. This prevents an infinite loop.
            break

def setup_telegram_bot():
    """Configures and starts the Telegram bot."""
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    # Message handler
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    app.add_handler(message_handler)

    return app

# --- Bot startup (to be executed only if this file is run directly) ---
if __name__ == '__main__':
    app = setup_telegram_bot()
    app.run_polling()
