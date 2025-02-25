# 🧠 MemoGenius Server

## 📱 Personal Assistant with AI-powered features

MemoGenius is an intelligent personal assistant that helps you manage reminders and find information through natural language conversations. Built with Google Gemini AI, it provides a seamless experience across both Telegram and web interfaces.

## ✨ Features

- 🤖 Natural language interaction with AI assistant in English and Italian
- ⏰ Create, view, update, and delete reminders 
- 🧠 Store and retrieve personal memories using vector search
- 🔍 Search the web for real-time information
- 🔄 Synchronization between Telegram and web interface
- 🕒 Get current date and time information
- 🔔 Automatic reminder notifications

## 🛠️ Recent Improvements

- **Thread-safe Memory Management**: Enhanced singleton pattern with thread locks for ChromaDB initialization
- **Robust Function Handling**: Improved handling of multiple function calls in chat interactions
- **Internationalized Codebase**: Full English/Italian bilingual support
- **Enhanced Error Recovery**: Better handling of API failures and response validation
- **Optimized Vector Search**: Improved memory retrieval accuracy

## 🛠️ Technical Stack

### Backend
- FastAPI for REST API
- SQLite database for structured data persistence
- ChromaDB for vector storage and semantic search
- Google Gemini AI for natural language processing
- Python Telegram Bot for Telegram integration
- APScheduler for reminder scheduling

### Frontend
- React-based web interface: [React Client Link](../frontend/)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key

### Steps

1. Clone the repository:
   ``` 
   git clone https://github.com/andrea9293/memogenius.git
   cd memogenius
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the backend directory with:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. Run the application:
   ```
   python start_all.py
   ```

## 📱 Usage

### Telegram Interface
1. Start a chat with your bot on Telegram
2. Use the `/start` command to initialize
3. Interact naturally with the assistant
4. Use the `/key` command to get your web access key

### Web Interface
1. Visit the web interface
2. Enter your access key from Telegram
3. Enjoy the same functionalities through the web UI

## 📝 Example Commands

- "Remind me to call mom tomorrow at 6 PM"
- "Remember that my WiFi password is 12345"
- "What was my WiFi password again?"
- "Show all my reminders"
- "Search for the weather in New York"
- "What time is it now?"

## 🔧 Development

### Project Structure
- `backend/` - FastAPI server and core application logic
  - `.env` - Environment configuration with API keys
  - `requirements.txt` - Python dependencies
  - `start_all.py` - Main entry script to run all services
  
  - `app/` - Application modules
    - `main.py` - FastAPI application setup and API endpoints
    - `chat_handler.py` - AI conversation management with Gemini
    - `config.py` - Application settings and configuration
    - `database.py` - Database connection and session management
    - `dependencies.py` - FastAPI dependency injection helpers
    - `gemini_tools.py` - Tools for interaction with Google Gemini AI
    - `memory_db.py` - Vector database for storing personal information
    - `memory_tools.py` - Tools for interacting with the memory system
    - `models.py` - SQLAlchemy database models (User, Reminder)
    - `reminders.py` - CRUD operations for reminders
    - `scheduler.py` - Background job for sending reminder notifications
    - `schemas.py` - Pydantic models for data validation
    - `telegram_bot.py` - Telegram bot implementation
    - `users.py` - User management functions
    - `utils.py` - Utility functions for formatting data

  - `data/` - Data storage
    - `reminders.db` - SQLite database
    - `custom_rag/` - ChromaDB vector storage for personal memories

## 🌐 API Documentation

When the FastAPI server is running, access the API documentation at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## 📄 License

This project is licensed under the AGPLv3 License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👏 Acknowledgements

- [Google Gemini AI](https://ai.google.dev/)
- [Python Telegram Bot](https://python-telegram-bot.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [ChromaDB](https://www.trychroma.com/)