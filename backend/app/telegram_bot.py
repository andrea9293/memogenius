import html
import telegram
import tempfile
import os
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
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
    
    # Define tags to check for empty lines
    standalone_tags = [
        '<div>', '</div>', 
        '<p>', '</p>', 
        '<html>', '</html>', 
        '<body>', '</body>',
        '<head>', '</head>',
        '<ul>', '</ul>',
        '<ol>', '</ol>',
        '<!DOCTYPE html>'
    ]
    
    # Process each line
    processed_lines = []
    for line in lines:
        line_stripped = line.strip()
        
        # Check if line contains only a standalone tag
        if line_stripped in standalone_tags:
            continue  # Skip this line entirely
        
        # Apply normal replacements
        line = line.replace('<br>', '\n')
        line = line.replace('<br/>', '\n')
        line = line.replace('<br />', '\n')
        line = line.replace('<div>', '')
        line = line.replace('</div>', '')
        line = line.replace('<p>', '')
        line = line.replace('</p>', '')
        line = line.replace('<li>', '• ')
        line = line.replace('</li>', '')
        line = line.replace('<ul>', '')
        line = line.replace('</ul>', '')
        line = line.replace('<ol>', '')
        line = line.replace('</ol>', '')
        line = line.replace('<html>', '')
        line = line.replace('</html>', '')
        line = line.replace('<body>', '')
        line = line.replace('</body>', '')
        line = line.replace('<strong>', '<b>')
        line = line.replace('</<strong>', '</b>')
        line = line.replace('<h1>', '<b>')
        line = line.replace('</h1>', '</b>')
        line = line.replace('<h2>', '<b>')
        line = line.replace('</h2>', '</b>')
        line = line.replace('<h3>', '<b>')
        line = line.replace('</h3>', '</b>')
        line = line.replace('<code>', '')
        line = line.replace('</code>', '')
        line = line.replace('<head>', '')
        line = line.replace('</head>', '')
        line = line.replace('<!DOCTYPE html>', '')
        
        processed_lines.append(line)
    
    text = '\n'.join(processed_lines)
    
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
    
    # Remove any resulting empty lines after processing
    lines = text.splitlines()
    lines = [line for line in lines if line.strip()]
    text = '\n'.join(lines)
    
    return text.strip()

def save_response_to_html(text: str) -> str:
    """Saves the response text to an HTML file and returns the file path"""
    # Create a temporary file with HTML extension
    fd, path = tempfile.mkstemp(suffix='.html')
    
    # Create a complete HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MemoGenius Response</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            blockquote {{ background-color: #f9f9f9; border-left: 5px solid #ccc; margin: 1.5em 10px; padding: 0.5em 10px; }}
            pre {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            code {{ background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }}
        </style>
    </head>
    <body>
    {text}
    </body>
    </html>
    """
    
    # Write the content to the file
    with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
        tmp.write(html_content)
    
    return path

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles errors during update processing"""
    error = context.error
    
    if isinstance(error, BadRequest) and "Message is too long" in str(error):
        if update.effective_message and hasattr(context, 'bot_data') and 'last_response' in context.bot_data:
            # Retrieve the complete original message
            original_text = context.bot_data['last_response']
            
            # Save the response to an HTML file
            file_path = save_response_to_html(original_text)
            
            # Send a brief message with the attached document
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="The response is too long to be sent as a message. Here's a document with the complete response:",
                parse_mode=ParseMode.HTML
            )
            
            # Send the document
            with open(file_path, 'rb') as document:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=document,
                    filename="complete_response.html"
                )
            
            # Delete the temporary file
            os.unlink(file_path)
    else:
        # For other types of errors, log the error
        original_text = ''
        if update.effective_message and hasattr(context, 'bot_data') and 'last_response' in context.bot_data:
            original_text = context.bot_data['last_response']
            
        print(f"An error occurred: {error} while processing the message. Please try again. \n\n{original_text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {error} while processing the message Please try again \n\n{html.escape(original_text)}",
            parse_mode=ParseMode.HTML
        )
        print(f"Unhandled error: {error}")

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
        text=welcome_message,
        parse_mode=ParseMode.HTML
    )

async def restart_gemini(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to restart Gemini AI"""
    user_id = get_user_id(update)
    db = SessionLocal()
    try:
        user = get_or_create_telegram_user(db, user_id)
        chat_handler.setup_chat()
        message = "the instance of Gemini AI has been restarted."
    finally:
        db.close()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
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
    response = await chat_handler.handle_message(update.message.text, user_id)
    
    if response.get("text"):
        # Save the original response in the bot data for potential use in the error handler
        context.bot_data['last_response'] = response["text"]
        
        try:
            print(f"Sending response: {response['text']}")
            formatted_text = escape_html(response["text"])
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=formatted_text,
                parse_mode=ParseMode.HTML
            )
        except BadRequest as e:
            if "Message is too long" in str(e):
                # Save the response to an HTML file
                file_path = save_response_to_html(response["text"])
                
                # Send a brief message with the attached document
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="La risposta è troppo lunga per essere inviata come messaggio. Ecco un documento con la risposta completa:",
                    parse_mode=ParseMode.HTML
                )
                
                # Send the document
                with open(file_path, 'rb') as document:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=document,
                        filename="risposta_completa.html"
                    )
                
                # Delete the temporary file
                os.unlink(file_path)
            else:
                # Raise the exception if it's of another type
                raise

def setup_telegram_bot():
    """Configures and initializes the Telegram bot with necessary handlers"""
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Aggiungi il gestore degli errori
    app.add_error_handler(error_handler)

    # Register command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('key', show_key))
    app.add_handler(CommandHandler('restartai', restart_gemini))
    
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
