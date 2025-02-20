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

def run_scheduler():
    """Esegue lo scheduler dei promemoria."""
    import app.scheduler  # Import solo qui per avviare lo scheduler
    # Il processo rimane attivo finché lo scheduler è in esecuzione
    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    # Crea i processi
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    telegram_process = multiprocessing.Process(target=run_telegram)
    scheduler_process = multiprocessing.Process(target=run_scheduler)

    # Avvia i processi
    fastapi_process.start()
    telegram_process.start()
    scheduler_process.start()

    try:
        fastapi_process.join()
        telegram_process.join()
        scheduler_process.join()
    except KeyboardInterrupt:
        print("\nArresto in corso...")
        fastapi_process.terminate()
        telegram_process.terminate()
        scheduler_process.terminate()
        fastapi_process.join()
        telegram_process.join()
        scheduler_process.join()
        print("Applicazione terminata.")
