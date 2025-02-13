
# **Spiegazione del codice `start_all.py`:**
# 1. **Importazioni:**
#    - `multiprocessing`: gestione processi paralleli
#    - `uvicorn`: server ASGI per FastAPI
#    - Importazione delle app esistenti

# 2. **Funzioni wrapper:**
#    - `run_fastapi()`: avvia il server FastAPI
#    - `run_telegram()`: avvia il bot Telegram

# 3. **Gestione processi:**
#    - Creazione processi separati per FastAPI e Telegram
#    - Avvio parallelo dei processi
#    - Gestione pulita dell'interruzione con try/except

# 4. **Vantaggi di questo approccio:**
#    - Isolamento dei processi
#    - Gestione indipendente delle risorse
#    - Terminazione pulita
#    - Facilità di debug
# Per utilizzare questa configurazione, basta eseguire `python start_all.py` dalla root del progetto.


import multiprocessing
import uvicorn
from app.telegram_bot import setup_telegram_bot
from app.main import app as fastapi_app

def run_fastapi():
    """Esegue il server FastAPI."""
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)

def run_telegram():
    """Esegue il bot Telegram."""
    app = setup_telegram_bot()
    app.run_polling()

if __name__ == "__main__":
    # Crea i processi
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    telegram_process = multiprocessing.Process(target=run_telegram)

    # Avvia i processi
    fastapi_process.start()
    telegram_process.start()

    try:
        # Attendi che i processi terminino (se necessario)
        fastapi_process.join()
        telegram_process.join()
    except KeyboardInterrupt:
        # Gestione pulita dell'interruzione (Ctrl+C)
        print("\nArresto in corso...")
        fastapi_process.terminate()
        telegram_process.terminate()
        fastapi_process.join()
        telegram_process.join()
        print("Applicazione terminata.")
