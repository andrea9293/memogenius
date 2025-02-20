# MemoGenius

MemoGenius is an intelligent personal assistant based on Telegram that helps you manage your reminders and much more. Powered by Gemini AI, it is capable of understanding your requests in natural language, creating contextual reminders, and providing informed responses thanks to Retrieval-Augmented Generation (RAG).

## ✨ Features

* 📝 **Intelligent Reminder Management**
  * Create, view, modify, and delete reminders
  * Natural language understanding
  * Contextual suggestions
  * Automatic notifications when reminders are due

* 🔍 **Advanced Search (RAG)**
  * Web search via Google Custom Search (Gemini 2.0 tool)
  * Vector database (ChromaDB) (work in progress...)
  * Custom text files (work in progress...)

* 🤖 **Artificial Intelligence**
  * Gemini model for language processing
  * Contextual and relevant answers
  * CrewAI for agent orchestration (work in progress...)
  * HTML formatted responses

* 💬 **Telegram Interface**
  * Easy to use
  * Accessible everywhere
  * Real-time responses

## 🏗 Architecture

The system is built on modern and reliable components:

* **Frontend:** Telegram Bot
* **Backend:** FastAPI Server
* **Database:**
  * SQLite for structured data
  * ChromaDB for vectors
* **AI:**
  * Gemini API
  * CrewAI
* **Scheduler:**
  * APScheduler for reminder notifications

## 📋 Prerequisites

* Python 3.9+
* Telegram Bot Token (from BotFather)
* Gemini API Key

## 🚀 Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/andrea9293/memogenius.git
    cd memogenius
    ```

2. Create the virtual environment:
    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    * Windows:
        ```bash
        venv\Scripts\activate
        ```
    * macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Configure the environment variables:
   Create a `.env` file in the root of the project:
    ```plaintext
    TELEGRAM_BOT_TOKEN=<YOUR_TELEGRAM_TOKEN>
    GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
    ```

## 🎯 Execution
### Activate the virtual environment
    
* Windows:
```bash
venv\Scripts\activate
```
* macOS/Linux:
```bash
source venv/bin/activate
```
### Unified Startup (Recommended)
Start both the FastAPI server and the Telegram bot with a single command:
```bash
python start_all.py
```

### Separate Startup

1. Telegram Bot Startup
```bash
python -m app.telegram_bot
```

2. FastAPI Server Startup
```bash
uvicorn app.main:app --reload
```

## 📁 Project Structure
```
memogenius/
├── app/                 # Application core
│   ├── __init__.py
│   ├── main.py         # FastAPI entry point
│   ├── config.py       # Configurations
│   ├── telegram_bot.py # Telegram Bot
│   ├── reminders.py    # Reminder management
│   ├── rag.py         # RAG Module
│   ├── agents.py      # CrewAI Agents
│   ├── models.py      # Database models
│   ├── utils.py       # Utilities
│   ├── database.py    # DB Connection
│   ├── scheduler.py   # Reminder scheduler
│   └── schemas.py     # Pydantic Schemas
│
├── data/               # Local data
│   ├── reminders.db   # SQLite Database
│   └── custom_rag/    # Files for RAG
│
├── tests/             # Tests
├── .env              # Configuration
├── requirements.txt  # Dependencies
├── README.md        # Documentation
└── .gitignore      # Git ignore
```

## 🌐 API Documentation

When the FastAPI server is running, access the API documentation at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.


## 📄 License
This project is distributed under the AGPLv3 License.  
See: [AGPLv3 License](https://www.gnu.org/licenses/agpl-3.0.en.html)  


