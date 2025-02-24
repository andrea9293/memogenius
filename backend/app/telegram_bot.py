import html
import telegram
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .config import settings
from .chat_handler import ChatHandler
from .database import SessionLocal
from .users import get_or_create_telegram_user

# Initialize ChatHandler
chat_handler = ChatHandler()

def get_user_id(update: telegram.Update) -> int:
    """Extracts the user ID from a Telegram Update object"""
    return update.effective_user.id

def escape_html(text: str) -> str:
    """
    Handles text formatting for Telegram HTML parsing
    Removes invalid tags and preserves valid HTML formatting
    """
    # Remove lines containing code blocks
    lines = text.splitlines()
    lines = [line for line in lines if '```' not in line]
    text = '\n'.join(lines)
    
    # Replace HTML tags with appropriate formatting
    text = text.replace('<br>', '\n')
    text = text.replace('<br/>', '\n')
    text = text.replace('<br />', '\n')
    text = text.replace('<div>', '')
    text = text.replace('</div>', '')
    text = text.replace('<li>', '• ')
    text = text.replace('</li>', '\n')
    text = text.replace('<ul>', '\n')
    text = text.replace('</ul>', '\n')
    
    # Escape special characters while preserving valid HTML
    text = html.escape(text)
    
    # Restore valid HTML tags for Telegram
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
    """Handles the /start command and provides access key"""
    user_id = get_user_id(update)
    db = SessionLocal()
    try:
        user = get_or_create_telegram_user(db, user_id)
        welcome_message = (
            "<b>Welcome to MemoGenius!</b>\n\n"
            "I'm your personal assistant. I can help you:\n"
            "• Create reminders\n"
            "• View your appointments\n"
            "• Modify or delete reminders\n"
            "• Search information on the web\n\n"
            f"Your access key for the web interface is:\n<code>{user.access_key}</code>\n\n"
            "<i>Tell me what I can do for you!</i>\n"
        )
    finally:
        db.close()

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=escape_html(welcome_message),
        parse_mode=ParseMode.HTML
    )

async def show_key(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to show access key"""
    user_id = get_user_id(update)
    db = SessionLocal()
    try:
        user = get_or_create_telegram_user(db, user_id)
        message = f"Your access key is:\n<code>{user.access_key}</code>"
    finally:
        db.close()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode=ParseMode.HTML
    )

async def handle_message(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes user messages using ChatHandler and sends responses"""
    user_id = get_user_id(update)
    # Rimuoviamo il parametro is_telegram che non è atteso
    response = await chat_handler.handle_message(update.message.text, user_id)
    
    if response.get("text"):
        formatted_text = escape_html(response["text"])
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=formatted_text,
            parse_mode=ParseMode.HTML
        )

def setup_telegram_bot():
    """Configures and initializes the Telegram bot with necessary handlers"""
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('key', show_key))
    
    # Register message handler for text messages
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), 
        handle_message
    ))

    return app

# Bot startup entry point
if __name__ == '__main__':
    app = setup_telegram_bot()
    app.run_polling()
