# 🧠 MemoGenius Server

## 📱 Personal Assistant with AI-powered features

MemoGenius is an intelligent personal assistant that helps you manage reminders and find information through natural language conversations. Built with Google Gemini AI, it provides a seamless experience across Telegram, web interfaces, and now Alexa devices.

## ✨ Features

- 🤖 Natural language interaction with AI assistant in English and Italian
- ⏰ Create, view, update, and delete reminders 
- 🧠 Store and retrieve personal memories using vector search
- 🔍 Search the web for real-time information
- 🔄 Synchronization between Telegram, web interface, and Alexa
- 🕒 Get current date and time information
- 🔔 Automatic reminder notifications
- 🔊 Voice interaction via Amazon Alexa devices

## 🛠️ Recent Improvements

- **Alexa Integration**: Full support for Amazon Alexa, allowing voice interaction with MemoGenius
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
- Amazon Alexa Skills Kit for voice interaction
- APScheduler for reminder scheduling

### Frontend
- React-based web interface: [React Client Link](../frontend/)
- Alexa voice interface for Echo devices

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token
- Google Gemini API Key
- Amazon Developer Account (for Alexa integration)

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

### Alexa Interface
1. Configure the Alexa Skill as described in the integration guide
2. Invoke the skill with "Alexa, open memo genius"
3. Interact naturally by speaking your requests
4. Use phrases like "memo genius what are my reminders" for best results

## 📝 Example Commands

### Text Commands (Telegram & Web)
- "Remind me to call mom tomorrow at 6 PM"
- "Remember that my WiFi password is 12345"
- "What was my WiFi password again?"
- "Show all my reminders"
- "Search for the weather in New York"
- "What time is it now?"

### Voice Commands (Alexa)
- "Alexa, open memo genius"
- "memo genius what are my reminders"
- "neko remind me to buy milk tomorrow"
- "memo genius search for the latest news about AI"
- "memo genius add pasta to my shopping list"

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

## 🎤 Alexa Integration

MemoGenius now offers full integration with Amazon Alexa, allowing voice interaction with the assistant. 

### Setup Requirements
- Amazon Developer Account
- Cloudflare account (for tunnel setup)
- Public domain name

### Configuration Steps
1. Set up a Cloudflare tunnel to expose your local server
2. Create a new Alexa Skill in the Amazon Developer Console
3. Configure the interaction model with the provided JSON
4. Set the endpoint to your server's Alexa endpoint
5. Test and publish your skill

For detailed instructions, refer to the integration guide in [MEMOGENIUS_ALEXA_INTEGRATION_GUIDE.md](./MEMOGENIUS_ALEXA_INTEGRATION_GUIDE.md).

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
- [Amazon Alexa Skills Kit](https://developer.amazon.com/en-US/alexa/alexa-skills-kit)